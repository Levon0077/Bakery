from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem, Product
from django.contrib import messages


def index(request):
    return render(request, 'bakery/index.html')

def product_list(request):
    products = Product.objects.all()
    return render(request, 'bakery/product_list.html', {'products': products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'bakery/product_detail.html', {'product': product})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1
    else:
        cart[product_id_str] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': 1
        }

    request.session['cart'] = cart
    return redirect('product_detail', pk=product_id)


def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for item_id, item in cart.items():
        subtotal = float(item['price']) * item['quantity']
        total += subtotal
        cart_items.append({
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'subtotal': subtotal,
        })

    return render(request, 'bakery/cart.html', {'cart_items': cart_items, 'total': total})


def clear_cart(request):
    request.session['cart'] = {}
    return redirect('cart')

@login_required
def checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Ваша корзина пуста.')
        return redirect('product_list')

    if request.method == 'POST':
        full_name = request.POST['full_name']
        address = request.POST['address']
        phone = request.POST['phone']

        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            address=address,
            phone=phone,
            status='В процессе'
        )

        total_price = 0
        for item_id, item in cart.items():
            product = Product.objects.get(id=item_id)
            total_price += float(item['price']) * item['quantity']
            OrderItem.objects.create(
                order=order,
                product=product,
                price=item['price'],
                quantity=item['quantity']
            )

        order.total_price = total_price
        order.save()

        request.session['cart'] = {}

        messages.success(request, f'Заказ #{order.id} успешно оформлен!')

        return redirect('order_history')

    return render(request, 'bakery/checkout.html')

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'bakery/order_history.html', {'orders': orders})


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    order.delete()

    from django.contrib import messages
    messages.success(request, f'Заказ #{order_id} успешно отменён.')
    return redirect('order_history')
