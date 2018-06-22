from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Cart
from orders.models import Order
from products.models import Product
from accounts.forms import LoginForm, GuestForm
from billing.models import BillingProfile
from addresses.forms import AddressForm
from addresses.models import Address


def cart_detail_api_view(request):
    cart_object, new_object = Cart.objects.new_or_get(request)
    products = [
        {
        'id': x.id,
        'url': x.get_absolute_url(),
        'name': x.title,
        'price': x.price
        } for x in cart_object.products.all()]

    cart_data = {'products': products, "total": cart_object.total}
    return JsonResponse(cart_data)


def cart_home(request):
    cart_object, new_object = Cart.objects.new_or_get(request)

    return render(request, 'cart/home_cart.html', {"cart": cart_object})


def cart_update(request):
    product_id = request.POST.get('product')

    if product_id is not None:
        try:
            product_object = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            print('Данный продукт отсутствует')
            return redirect('cart:cart_home')
        cart_object, new_object = Cart.objects.new_or_get(request)
        if product_object in cart_object.products.all():
            cart_object.products.remove(product_object)
            added = False
        else:
            cart_object.products.add(product_object)
            added = True
        request.session['cart_items'] = cart_object.products.count()
        if request.is_ajax():
            print('Ajax request')
            json_data = {
                "added": added,
                'removed': not added,
                'cartItemCount': cart_object.products.count()
            }
            return JsonResponse(json_data, status=200)
            #return JsonResponse({'message': 'Error 400'}, status_code=400)
    return redirect("cart:cart_home")


def checkout_home(request):
    cart_object, cart_created = Cart.objects.new_or_get(request)
    order_object = None
    if cart_created or cart_object.products.count() == 0:
        return redirect("cart:cart_home")

    login_form = LoginForm()
    guest_form = GuestForm()
    address_form = AddressForm()
    billing_address_id = request.session.get("billing_address_id", None)
    shipping_address_id = request.session.get("shipping_address_id", None)

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    address_qs = None
    if billing_profile is not None:
        if request.user.is_authenticated():
            address_qs = Address.objects.filter(billing_profile=billing_profile)
        order_object, order_object_created = Order.objects.new_or_get(billing_profile, cart_object)
        if shipping_address_id:
            order_object.shipping_address = Address.objects.get(id=shipping_address_id)
            del request.session["shipping_address_id"]
        if billing_address_id:
            order_object.billing_address = Address.objects.get(id=billing_address_id)
            del request.session["billing_address_id"]
        if billing_address_id or shipping_address_id:
            order_object.save()

    if request.method == "POST":
        "check that order is done"
        is_done = order_object.check_done()
        if is_done:
            order_object.mark_paid()
            request.session['cart_items'] = 0
            del request.session['cart_id']
            return redirect("cart:checkout_success")

    context = {
        "order": order_object,
        "billing_profile": billing_profile,
        "login_form": login_form,
        "guest_form": guest_form,
        "address_form": address_form,
        'address_qs': address_qs
    }
    return render(request, "cart/checkout.html", context)


def checkout_done(request):
    return render(request, "cart/checkout_done.html", {})
