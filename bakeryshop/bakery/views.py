from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Order, OrderItem, Category
def index(request):
    return render(request, 'bakery/index.html')

def product_list(request):
    category_slug = request.GET.get('category')
    sort_option = request.GET.get('sort')

    products = Product.objects.all()
    categories = Category.objects.all()

    if category_slug:
        products = products.filter(category__slug=category_slug)

    if sort_option == 'name':
        products = products.order_by('name')
    elif sort_option == 'name_desc':
        products = products.order_by('-name')
    elif sort_option == 'price_asc':
        products = products.order_by('price')
    elif sort_option == 'price_desc':
        products = products.order_by('-price')

    return render(request, 'bakery/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': category_slug,
        'sort_option': sort_option,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'bakery/product_detail.html', {'product': product})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += quantity
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': float(product.price),
            'quantity': quantity,
        }

    request.session['cart'] = cart
    return redirect('cart')


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
