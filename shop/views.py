from django.shortcuts import render,  get_object_or_404
from .models import Product
from django.shortcuts import redirect
from .forms import CheckoutForm

# Create your views here.

def home(request):
    products = Product.objects.all()
    return render(request, "shop/home.html", {"products": products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})


def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = request.session.get('cart', {})

    if str(pk) in cart:
        cart[str(pk)] += 1
    else:
        cart[str(pk)] = 1

    request.session['cart'] = cart
    return redirect('cart_detail')


def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    cart_total = 0

    for pk, qty in cart.items():
        product = get_object_or_404(Product, pk=pk)
        cart_items.append({'product': product, 'quantity': qty})
        cart_total += product.price * qty

    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'cart_total': cart_total})


def update_cart(request, pk):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart[str(pk)] = quantity
        else:
            cart.pop(str(pk), None)
        request.session['cart'] = cart
    return redirect('cart_detail')


def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    cart.pop(str(pk), None)
    request.session['cart'] = cart
    return redirect('cart_detail')

def checkout(request):
    cart = request.session.get('cart', {})
    cart_items = []
    cart_total = 0

    for pk, qty in cart.items():
        product = get_object_or_404(Product, pk=pk)
        cart_items.append({'product': product, 'quantity': qty})
        cart_total += product.price * qty

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.total = cart_total
            order.save()
            request.session['cart'] = {}  # empty cart after order
            return render(request, 'shop/checkout_success.html', {'order': order})
    else:
        form = CheckoutForm()

    return render(request, 'shop/checkout.html', {'cart_items': cart_items, 'cart_total': cart_total, 'form': form})