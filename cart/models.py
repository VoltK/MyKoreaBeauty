from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save, m2m_changed
from products.models import Product

User = settings.AUTH_USER_MODEL


# class CartManager(models.Manager):
#     def new_or_get(self, request):
#         cart_id = request.session.get('cart_id', None)
#         qs = self.get_queryset().filter(id=cart_id)
#         if qs.count() == 1:
#             new_object = False
#             cart_object = qs.first()
#             if request.user.is_authenticated() and cart_object.user is None:
#                 cart_object.user = request.user
#                 cart_object.save()
#         else:
#             cart_object = Cart.objects.new(user=request.user)
#             new_object = True
#             request.session['cart_id'] = cart_object.id
#         return cart_object, new_object
#
#     def new(self, user=None):
#         user_object = None
#         if user is not None:
#             if user.is_authenticated():
#                 user_object = user
#         return self.model.objects.create(user=user_object)

class CartManager(models.Manager):
    def new_or_get(self, request):
        cart_id = request.session.get("cart_id", None)
        qs = self.get_queryset().filter(id=cart_id)
        if qs.count() == 1:
            new_object = False
            cart_object = qs.first()
            if request.user.is_authenticated() and cart_object.user is None:
                user_cart = self.model.objects.filter(user=request.user).first()
                if user_cart is not None:
                    cart_object.products.add(*user_cart.products.all())
                    cart_object.user = request.user
                    cart_object.save()
                    user_cart.delete()
                else:
                    cart_object.user = request.user
                    cart_object.save()
        else:
            cart_object = Cart.objects.new(user=request.user)
            new_object = True
            request.session['cart_id'] = cart_object.id
        return cart_object, new_object

    def new(self, user=None):
        user_object = None
        if user is not None:
            if user.is_authenticated():
                cart_object = self.model.objects.filter(user=user).first()
                if cart_object is not None:
                    return cart_object
                user_object = user
        return self.model.objects.create(user=user_object)


class Cart(models.Model):
    user     = models.ForeignKey(User, null=True, blank=True)
    products = models.ManyToManyField(Product, blank=True)
    total    = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    updated  = models.DateTimeField(auto_now=True)
    timestamp= models.DateTimeField(auto_now_add=True)

    objects = CartManager()

    def __str__(self):
        return str(self.id)


def m2m_changed_cart_receiver(sender, instance, action, *args, **kwargs):
    if action == 'post_add' or action == 'post_remove' or action == 'post_clear':
        products = instance.products.all()
        total = 0
        for x in products:
            total += x.price
        instance.total = total
        instance.save()


m2m_changed.connect(m2m_changed_cart_receiver, sender=Cart.products.through)
