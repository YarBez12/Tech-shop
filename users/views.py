from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, user_logged_in
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import FormView
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from .forms import *
from django.views.generic import CreateView
from carts.models import Cart, Receiver
from products.models import Product, FavouriteProduct, ProductImage, Subcription
from django.db.models.functions import Lower
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.views.generic.edit import FormMixin
from products.forms import ProductForm
from datetime import timedelta
from django.utils import timezone
from users.models import Action, NotificationState
from django.contrib.contenttypes.models import ContentType
import redis
from django.conf import settings
from .tasks import send_email_task

r = redis.Redis(host=settings.REDIS_HOST,
 port=settings.REDIS_PORT,
 db=settings.REDIS_DB)

def get_user_favourites(user_id):
    return r.smembers(f'favourite:user:{user_id}')



class UserLoginView(LoginView):
    form_class = LoginForm
    template_name = 'users/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next') or self.request.POST.get('next', '')
        context['title'] = 'Login'
        return context
    def get_success_url(self):
        redirect_page = self.request.POST.get('next', None)
        if redirect_page and redirect_page != reverse('users:logout'):
            return redirect_page
        return reverse_lazy('main:index')
    
    def form_valid(self, form):
        session_key = self.request.session.session_key
        user = form.get_user()
        if user:
            login(self.request, user)
            merge_carts(session_key, user)
            remember_me = self.request.POST.get('remember_me')
            if remember_me:
                self.request.session.cycle_key()
                self.request.session.set_expiry(2592000)
            else:
                self.request.session.set_expiry(0)
            messages.success(self.request, f"{user.first_name}, You successfuly logined")
            return redirect(self.get_success_url())
    
    def form_invalid(self, form):
        error_messages = []
        for field, errors in form.errors.items():
            field_label = field if field != '__all__' else 'General'
            error_messages.append(f"{field_label}: {', '.join(errors)}")
        full_error_message = "Please correct the following errors: " + "; ".join(error_messages)
        messages.error(self.request, full_error_message)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

class UserRegistrationView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'users/registration.html'

    def get_success_url(self):
        return reverse_lazy('main:index')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Registration'
        context['address_form'] = AddressForm()
        return context
    
    def post(self, request, *args, **kwargs):
        user_form = self.get_form()
        address_checked = request.POST.get('show-address')  == 'on'
        
        if user_form.is_valid():
            if address_checked:
                address_form = AddressForm(data = request.POST)
                if address_form.is_valid():
                    return self.form_valid(user_form, address_form)
                else:
                    return self.form_invalid(user_form, address_form)
            else:
                return self.form_valid(user_form)
        else:
            return self.form_invalid(user_form, None)

    
    def form_valid(self, user_form, address_form = None):
        user = user_form.save(commit=False)
        if user:
            if address_form:
                address_data = address_form.cleaned_data
                address, created = Address.objects.get_or_create(**address_data)
                user.address = address
            session_key = self.request.session.session_key
            merge_carts(session_key, user)
            user.save()
            login(self.request, user)
            remember_me = self.request.POST.get('remember_me')
            if remember_me:
                self.request.session.cycle_key()
                self.request.session.set_expiry(2592000)
            else:
                self.request.session.set_expiry(0)

        messages.success(self.request, 'You successfuly registered to your account')
        return redirect(self.get_success_url())
    
    def form_invalid(self, user_form, address_form = None):
        error_messages = []
        for form_instance in [user_form, address_form]:
            if form_instance:
                for field, errors in form_instance.errors.items():
                    field_label = field if field != '__all__' else 'General'
                    error_messages.append(f"{field_label}: {', '.join(errors)}")
        full_error_message = "Please correct the following errors: " + "; ".join(error_messages)
        messages.error(self.request, full_error_message)
        self.object = None
        if address_form:
            return self.render_to_response(self.get_context_data(form=user_form, address_form=address_form))
        else:
            return super().form_invalid(user_form)


def user_logout(request):
    logout(request)
    return redirect('main:index')



def merge_carts(session_key, user):
    if session_key:
        try:
            session_cart = Cart.objects.get(session_key=session_key, is_completed=False)
        except Cart.DoesNotExist:
            session_cart = None

        if session_cart:
            try:
                receiver = Receiver.objects.get(user= user)
                user_cart = Cart.objects.get(receiver = receiver, is_completed = False)
            except (Cart.DoesNotExist, Receiver.DoesNotExist):
                user_cart = None

            if user_cart:
                for ordered_product in session_cart.ordered.all():
                    user_ordered_product, created = user_cart.ordered.get_or_create(product=ordered_product.product)
                    if not created:
                        user_ordered_product.quantity += ordered_product.quantity
                    else:
                        user_ordered_product.quantity = ordered_product.quantity
                    user_ordered_product.save()
                session_cart.delete()
            else:
                receiver, _ = Receiver.objects.get_or_create(user=user)
                session_cart.receiver = receiver
                session_cart.session_key = None
                session_cart.save()

class ProfileView(LoginRequiredMixin, DetailView, FormMixin):
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'user'
    form_class = ProductForm

    def get_object(self, queryset = ...):
        return self.request.user
    
    def get_success_url(self):
        return self.request.path_info
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        receiver, _ = Receiver.objects.get_or_create(user= user)
        cart, _ = Cart.objects.get_or_create(receiver = receiver, is_completed = False)
        completed_orders = Cart.objects.filter(receiver = receiver, is_completed = True).order_by('-date_completed')

        brand_ids = Subcription.objects.filter(user=user).values_list('brand_id', flat=True)
        two_weeks_ago = timezone.now() - timedelta(days=14)
        news = Product.objects.filter(brand_id__in=brand_ids, updated_at__gte=two_weeks_ago)

        session_key = "ui_state:profile"
        ui_state = self.request.session.get(session_key, {})
        sort_option = ui_state.get('sort', 'title')
        state, _ = NotificationState.objects.get_or_create(user=user)
        now = timezone.now()
        tab = ui_state.get('tab')
        if tab == 'news':
            state.last_seen_news = now
        elif tab == 'other_actions':
            state.last_seen_actions = now
        state.save() 
        context['saved_ui_state'] = ui_state
        # fav_products = user.favourite_products.all()
        # product_ids = fav_products.values_list('product__pk', flat=True)
        # products = Product.objects.filter(pk__in=product_ids, is_active=True)
        redis_product_ids = get_user_favourites(user.id)
        product_ids = [int(pid) for pid in redis_product_ids]
        products = Product.objects.filter(pk__in=product_ids, is_active=True)
        if sort_option:
            products = sort_with_option(sort_option, products)
        paginator = Paginator(products, 2)
        page = self.request.GET.get('page')
        try:
            paginated_products = paginator.page(page)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)

        user_products = user.products.filter(is_active=True)
        if sort_option:
            user_products = sort_with_option(sort_option, user_products)

        product_ct = ContentType.objects.get_for_model(Product)
        other_actions = Action.objects.filter(
            target_ct=product_ct,
            target_id__in=user_products.values_list('id', flat=True)
        ).exclude(user=user).select_related('user')
        
        context['title'] = 'Profile'
        context['page_obj'] = paginated_products
        context['cart'] = cart
        context['completed_orders'] = completed_orders
        context['products'] = paginated_products
        context['product_form'] = self.get_form()
        context['user_products'] = user_products
        context['news'] = news
        context['other_actions'] = other_actions


        return context
    

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.is_active = False
            product.save()
            form.save_m2m()
            images = request.FILES.getlist('images')
            for image in images:
                ProductImage.objects.create(product=product, image=image)
            messages.success(self.request, 'Your product has been succesfully added')
            return self.form_valid(form)
        else:
            error_messages = []
            for field, errors in form.errors.items():
                field_label = field if field != '__all__' else 'General'
                error_messages.append(f"{field_label}: {', '.join(errors)}")
            full_error_message = "Please correct the following errors: " + "; ".join(error_messages)
            messages.error(self.request, full_error_message)
            return self.form_invalid(form)
    
    
def sort_with_option(sort_option, items):
    if sort_option == 'title':
        items = items.annotate(lower_title=Lower('title')).order_by('lower_title')
    elif sort_option == '-title':
        items = items.annotate(lower_title=Lower('title')).order_by('-lower_title')
    else:
        items = items.order_by(sort_option)
    return items


class UserEditView(View):
    template_name = 'users/user_edit.html'
    
    def get_context_data(self, **kwargs):
        context = {}
        context['user_form'] = UserEditForm(instance=self.request.user)
        address_instance = self.request.user.address
        if address_instance:
            context['address_form'] = AddressForm(instance=address_instance)
        else:
            context['address_form'] = AddressForm()
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user_form = UserEditForm(request.POST, instance=self.request.user)
        address_form = AddressForm(request.POST, instance=self.request.user.address)
        if user_form.is_valid() and address_form.is_valid():
            user = request.user
            user_data = user_form.cleaned_data
            address_data = address_form.cleaned_data
            address, _ = Address.objects.get_or_create(**address_data)
            user_data['address'] = address
            for field, value in user_data.items():
                setattr(user, field, value)
            user.save()
            messages.success(request, "User's information has been changed!")
            return redirect(reverse_lazy('users:profile'))  
        else:
            context = self.get_context_data()
            context['user_form'] = user_form
            context['address_form'] = address_form
            error_messages = []
            for form_instance in [user_form, address_form]:
                if form_instance:
                    for field, errors in form_instance.errors.items():
                        field_label = field if field != '__all__' else 'General'
                        error_messages.append(f"{field_label}: {', '.join(errors)}")
            full_error_message = "Please correct the following errors: " + "; ".join(error_messages)
            messages.error(self.request, full_error_message)
            return render(request, self.template_name, context)
        


class SendMainView(FormView):
    template_name = 'users/send_mail.html'
    form_class = MailForm
    success_url = reverse_lazy('main:index')  
    extra_context = {'title' : 'Sending email'}

    def form_valid(self, form):
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        html_message = form.cleaned_data.get('html_message', '')
        recipients = list(User.objects.all().values_list('email', flat=True))
        
        for recipient in recipients:
            send_email_task.delay(subject, message, html_message, recipient)
        return super().form_valid(form)
    
