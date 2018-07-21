from django.conf.urls import url
from .views import OrderListView, OrderDetailView

urlpatterns = [
    url(r'^$', OrderListView.as_view(), name='order_list'),
    url(r'^(?P<order_id>[0-9A-Za-z]+)/$', OrderDetailView.as_view(), name='order_details'),
]
