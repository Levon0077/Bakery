from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Order, OrderItem


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
        return redirect('order_error')

    if request.method == 'POST':
        try:
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

            return redirect('order_success')

        except Exception as e:
            print("Ошибка оформления:", e)
            return redirect('order_error')

    return render(request, 'bakery/checkout.html')


@login_required
def order_history(request):
    selected_status = request.GET.get('status')
    orders = Order.objects.filter(user=request.user)
    if selected_status:
        orders = orders.filter(status=selected_status)
    return render(request, 'bakery/order_history.html', {'orders': orders, 'selected_status': selected_status})


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.delete()
    messages.success(request, f'Заказ #{order_id} был отменён.')
    return redirect('order_history')


def order_success(request):
    return render(request, 'bakery/order_success.html')


def order_error(request):
    return render(request, 'bakery/order_error.html')
