from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import ReviewForm
from .models import Product, Order, OrderItem, Category

def index(request):
    featured_categories = Category.objects.filter(is_featured=True)[:3]
    popular_products = Product.objects.order_by('-purchase_count')[:8]
    limited_products = Product.objects.filter(is_limited=True)[:5]
    products = Product.objects.all()[:3]

    return render(request, 'bakery/index.html', {
        'products': products,
        'featured_categories': featured_categories,
        'popular_products': popular_products,
        'limited_products': limited_products,
    })

def product_list(request):
    products = Product.objects.all()

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

    # Сортировка
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'popularity':
        products = products.order_by('-popularity')
    elif sort == 'rating':
        products = sorted(products, key=lambda p: p.average_rating(), reverse=True)
    elif sort == 'newest':
        products = products.order_by('-created_at')

    context = {
        'products': products,
        'sort': sort,
        'min_price': min_price,
        'max_price': max_price,
        'search_query': search_query,
    }
    return render(request, 'bakery/product_list.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all().order_by('-created_at')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('product_detail', pk=pk)
    else:
        form = ReviewForm()

    return render(request, 'bakery/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form,
    })


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
