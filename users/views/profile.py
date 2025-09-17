from users.models import User, NotificationState, Action, Address
from carts.models import Cart, Receiver
from django.contrib.contenttypes.models import ContentType
from products.forms import ProductForm
from products.models import Product, ProductImage, Subcription, Brand
from datetime import timedelta
from django.utils import timezone
from users.utils import get_user_favourites, build_form_errors_html
from products.utils.filters import sort_with_option
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from users.forms import UserEditForm, AddressForm
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, View
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin





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
        cart = Cart.objects.get_or_create_with_session(self.request, receiver = receiver, is_completed = False)
        completed_orders = Cart.objects.filter(receiver = receiver, is_completed = True).order_by('-date_completed')
        subcriptions = Subcription.objects.filter(user=user).only('brand_id')
        brand_ids = subcriptions.values_list('brand_id', flat=True)
        brands = Brand.objects.filter(pk__in=brand_ids)
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
            state.save(update_fields=['last_seen_news'])
        elif tab == 'other_actions':
            state.last_seen_actions = now
            state.save(update_fields=['last_seen_actions'])
        redis_product_ids = get_user_favourites(user.id)
        try:
            product_ids = [int(pid) for pid in redis_product_ids]
        except Exception:
            product_ids = []
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

        user_products = user.products.select_related('brand').all()
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
        context['brands'] = brands
        context['saved_ui_state'] = ui_state


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
            messages.error(self.request, build_form_errors_html(form))
            return self.form_invalid(form)
    
    


class UserEditView(View):
    template_name = 'users/user_edit.html'
    
    def get_context_data(self, **kwargs):
        context = {}
        context['user_form'] = UserEditForm(instance=self.request.user)
        address_instance = self.request.user.address
        context['address_form'] = AddressForm(instance=address_instance) if address_instance else AddressForm()
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    @transaction.atomic
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
        context = self.get_context_data()
        context['user_form'] = user_form
        context['address_form'] = address_form
        messages.error(self.request, build_form_errors_html(user_form, address_form))
        return render(request, self.template_name, context)