from django.conf.urls import url
from .views import AccountHomeView, AccountEmailActivationView, UserDetailUpdateView
from products.views import UserHistoryProductView

urlpatterns = [
    url(r'^$', AccountHomeView.as_view(), name='home'),
    url(r'^details/$', UserDetailUpdateView.as_view(), name='update_profile'),
    url(r'^history/products$', UserHistoryProductView.as_view(), name='user_history'),

    url(r'^email/confirm/(?P<key>[0-9A-Za-z]+)/$',
                    AccountEmailActivationView.as_view(),
                    name='email-activate'),
    url(r'^email/resend-activation/$',
                    AccountEmailActivationView.as_view(),
                    name='resend-activation'),
]
