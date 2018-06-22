from django.conf.urls import url
from .views import cart_home, cart_update, checkout_home, checkout_done

urlpatterns = [
    url(r'^$', cart_home, name='cart_home'),
    url(r'^update/$', cart_update, name='cart_update'),
    url(r'^checkout/$', checkout_home, name='checkout'),
    url(r'^checkout/success/$', checkout_done, name='checkout_success'),

]
