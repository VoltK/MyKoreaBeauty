from django.db import models
from math import fsum
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save, post_save
from addresses.models import Address
from billing.models import BillingProfile
from cart.models import Cart
from my_korea.utils import unique_order_id_generator


ORDER_STATUS_CHOICES = (
    ('создан', 'Создан'),
    ('оплачено', 'Оплачено'),
    ('доставлено', 'Доставлено')
                         )


class OrderManagerQuerySet(models.query.QuerySet):
    def by_request(self, request):
        billing_profile, created = BillingProfile.objects.new_or_get(request)
        return self.filter(billing_profile=billing_profile)


class OrderManager(models.Manager):

    def get_queryset(self):
        return OrderManagerQuerySet(self.model, using=self._db)

    def by_request(self, request):
        return self.get_queryset().by_request(request)

    def new_or_get(self, billing_profile, cart_object):
        created = False
        order_qs = self.get_queryset().filter(billing_profile=billing_profile,
                                              cart=cart_object,
                                              active=True,
                                              status='создан')

        if order_qs.count() == 1:
            order_object = order_qs.first()
        else:
            order_object = self.model.objects.create(billing_profile=billing_profile, cart=cart_object)
            created = True
        return order_object, created


class Order(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, null=True, blank=True)
    order_id = models.CharField(max_length=120, blank=True)
    shipping_address = models.ForeignKey(Address, related_name="shipping", null=True, blank=True)
    billing_address = models.ForeignKey(Address, related_name="billing", null=True, blank=True)
    cart = models.ForeignKey(Cart)
    status = models.CharField(max_length=120, default='создан', choices=ORDER_STATUS_CHOICES)
    shipping_total = models.DecimalField(default=20.99, max_digits=100, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.order_id

    objects = OrderManager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def get_absolute_url(self):
        return reverse("orders:order_details", kwargs={'order_id': self.order_id})

    def update_total(self):
        cart_total = self.cart.total
        shipping_total = self.shipping_total
        new_total = fsum([cart_total, shipping_total])
        self.total = new_total
        self.save()
        return new_total

    def check_done(self):
        billing_profile = self.billing_profile
        shipping_address = self.shipping_address
        billing_address = self.billing_address
        total = self.total
        if billing_profile and shipping_address and billing_address and total > 0:
            return True
        return False

    def mark_paid(self):
        if self.check_done():
            self.status = "оплачено"
            self.save()

        return self.status


def pre_save_create_order_id(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)
    qs = Order.objects.filter(cart=instance.cart).exclude(billing_profile=instance.billing_profile)
    if qs.exists():
        qs.update(active=False)


pre_save.connect(pre_save_create_order_id, sender=Order)


def post_save_cart_total(sender, instance, created, *args, **kwargs):
    if not created:
        cart_object = instance
        cart_total = cart_object.total
        cart_id = cart_object.id
        qs = Order.objects.filter(cart__id=cart_id)
        if qs.count() == 1:
            order_object = qs.first()
            order_object.update_total()

post_save.connect(post_save_cart_total, sender=Cart)


def post_save_order(sender, instance, created, *args, **kwargs):
    print("running")
    if created:
        print("Updating... first")
        instance.update_total()


post_save.connect(post_save_order, sender=Order)

