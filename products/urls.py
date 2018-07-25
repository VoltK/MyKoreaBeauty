from django.conf.urls import url
from .views import product_list, ProductDetailView


urlpatterns = [
    url(r'^$', product_list, name='list'),
    url(r'^category/(?P<category_slug>[-\w]+)/$', product_list, name='list_by_category'),
    url(r'^(?P<id>\d+)/(?P<slug>[-\w]+)/$', ProductDetailView.as_view(), name="detail"),
]
