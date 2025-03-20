from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name = 'login'),
    path('registration/', UserRegistrationView.as_view(), name = 'registration'),
    path('logout/', user_logout, name = 'logout'),
    path('profile/', ProfileView.as_view(), name = 'profile'),
    path('user_edit/', UserEditView.as_view(), name = 'user_edit'),
    path('send_mail/', SendMainView.as_view(), name = 'send_mail'),
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset_form.html',
             success_url='done/',
             email_template_name='users/password_reset_email.html'
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html',
             success_url=reverse_lazy('users:password_reset_complete')
         ), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]