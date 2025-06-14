from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_avatar/', views.change_avatar, name='change_avatar'),
    path('change_password/', views.change_password, name='change_password'),
    path('confirm_old_password/', views.confirm_old_password, name='confirm_old_password'),
    path('password_change_done/', views.password_change_done, name='password_change_done'),
    path('send_test_email/', views.send_test_email, name='send_test_email'),
    path('confirm/<uidb64>/<token>/', views.confirm_registration, name='confirm_registration'),
]
