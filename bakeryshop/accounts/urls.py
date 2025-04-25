from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('confirm/<uidb64>/<token>/', views.confirm_registration, name='confirm_registration'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change_avatar/', views.change_avatar, name='change_avatar'),
]
