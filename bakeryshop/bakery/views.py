from django.shortcuts import render, get_object_or_404, redirect  # добавьте redirect
from .models import Product


# Главная страница — список товаров
def product_list(request):
    products = Product.objects.all()
    return render(request, 'bakery/product_list.html', {'products': products})


# Детали товара
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'bakery/product_detail.html', {'product': product})


# Добавление товара в корзину
def add_to_cart(request, product_id):
    # Получаем товар по ID
    product = Product.objects.get(id=product_id)

    # Логика добавления товара в корзину (например, через сессию)
    cart = request.session.get('cart', {})
    if product_id in cart:
        cart[product_id]['quantity'] += 1  # Увеличиваем количество, если товар уже в корзине
    else:
        cart[product_id] = {'name': product.name, 'price': str(product.price), 'quantity': 1}

    request.session['cart'] = cart  # Сохраняем корзину в сессию
    return redirect('product_detail', pk=product_id)  # Перенаправляем обратно на страницу товара


# Корзина (заглушка)
def cart_view(request):
    return render(request, 'bakery/cart.html')


# Оформление заказа (заглушка)
def checkout_view(request):
    return render(request, 'bakery/checkout.html')


# История заказов (заглушка)
def order_history(request):
    return render(request, 'bakery/order_history.html')
