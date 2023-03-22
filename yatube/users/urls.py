from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.views import PasswordChangeDoneView
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import PasswordResetDoneView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetCompleteView

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),

    # Выход из системы
    path('logout/',
         LogoutView.as_view(template_name='users/logged_out.html'),
         name='logout'),

    # Вход в систему
    path('login/',
         LoginView.as_view(template_name='users/login.html'),
         name='login'),

    # Страница изменения пароля
    path('password_change/',
         PasswordChangeView.
         as_view(template_name='users/password_change_form.html'),
         name='password_change'),

    # Подтверждение изменения пароля
    path('password_change/done/',
         PasswordChangeDoneView.
         as_view(template_name='users/password_change_done.html'),
         name='password_change_done'),

    # Сброс пароля по почте
    path('password_reset/',
         PasswordResetView.
         as_view(template_name='users/password_reset_form.html'),
         name='password_reset'),

    # Подтверждение сброса пароля
    path('password_reset/done/',
         PasswordResetDoneView.
         as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),

    # Страница с вводом нового пароля
    path('reset/<uidb64>/<token>/',
         PasswordResetConfirmView.
         as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),

    # Страница входа с после восстановления пароля
    path('reset/done/',
         PasswordResetCompleteView.
         as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
]
