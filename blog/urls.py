from django.conf.urls import url
from .views import post_list, PostDetailView

urlpatterns = [
    url(r'^$', post_list, name='post_list'),
    url(r'^(?P<category_slug>[-\w]+)/$', post_list, name='list_post_by_category'),
    url(r'^(?P<id>\d+)/(?P<slug>[-\w]+)/$', PostDetailView.as_view(), name="post_detail"),
]
