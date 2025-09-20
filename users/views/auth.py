from users.forms import LoginForm, UserRegistrationForm, AddressForm
from users.models import Address
from django.utils.http import url_has_allowed_host_and_scheme
from django.urls import reverse_lazy, reverse
from users.utils import apply_remember_me, merge_carts, build_form_errors_html
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from urllib.parse import urlsplit
from django.urls import resolve, Resolver404



class UserLoginView(LoginView):
    form_class = LoginForm
    template_name = 'users/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next') or self.request.POST.get('next', '')
        context['title'] = 'Login'
        return context
    def get_success_url(self):
        redirect_page = self.request.POST.get('next') or self.request.GET.get('next')
        if redirect_page and url_has_allowed_host_and_scheme(redirect_page, allowed_hosts={self.request.get_host()}) and redirect_page != reverse('users:logout'):
            path = urlsplit(redirect_page).path
            try:
                match = resolve(path)
                if match.namespace == 'carts' and match.url_name in {'checkout', 'payment'}:
                    return reverse('carts:cart')
            except Resolver404:
                pass
            return redirect_page
        return reverse_lazy('main:index')
    
    def form_valid(self, form):
        user = form.get_user()
        if user:
            login(self.request, user)
            apply_remember_me(self.request)
            messages.success(self.request, f"{user.first_name}, You successfuly logined")
            return redirect(self.get_success_url())
    
    def form_invalid(self, form):
        messages.error(self.request, build_form_errors_html(form))
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
            user.save()
            login(self.request, user)
            apply_remember_me(self.request)

        messages.success(self.request, 'You successfuly registered to your account')
        return redirect(self.get_success_url())
    
    def form_invalid(self, user_form, address_form = None):
        messages.error(self.request, build_form_errors_html(user_form, address_form))
        self.object = None
        if address_form:
            return self.render_to_response(self.get_context_data(form=user_form, address_form=address_form))
        else:
            return super().form_invalid(user_form)


def user_logout(request):
    logout(request)
    return redirect('main:index')