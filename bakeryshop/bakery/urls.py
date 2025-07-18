from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('product/<int:product_id>/add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('order/success/', views.order_success, name='order_success'),
    path('order/error/', views.order_error, name='order_error'),
    path('order/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
]

