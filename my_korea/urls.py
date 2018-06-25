"""my_korea URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.urls import reverse_lazy
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from accounts.views import LoginView, RegisterView, guest_register
from addresses.views import checkout_address_create_view, checkout_address_reuse_view
from .views import home_page, about_page, contact_page
from cart.views import cart_detail_api_view
from django.views.generic import RedirectView
from e_marketing.views import MailchimpWebhookView


urlpatterns = [
    url(r'^$', home_page, name='home'),
    url(r'^about/$', about_page, name='about'),
    url(r'^contact/$', contact_page, name='contact'),
    # редирект на кастомную url
    # url(r'^accounts/', RedirectView.as_view(url='/account')),
    # по дефолту в Джанге url идет /accounts/...
    url(r'^accounts/', include('accounts.urls', namespace='account')),
    url(r'^accounts/', include('accounts.passwords.urls')),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^register/guest/$', guest_register, name='guest_register'),
    url(r'^logout/$', LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^products/', include('products.urls', namespace='products')),
    url(r'^search/', include('search.urls', namespace='search')),
    url(r'^cart/', include('cart.urls', namespace='cart')),
    url(r'^api/cart/', cart_detail_api_view, name='api-cart'),
    url(r'^checkout/address/create/$', checkout_address_create_view, name='checkout_address_create'),
    url(r'^checkout/address/reuse/$', checkout_address_reuse_view, name='checkout_address_reuse'),
    url(r'^webhook/mailchimp/$', MailchimpWebhookView.as_view(), name='webhooks-mailchimp'),
    url(r'^settings/', RedirectView.as_view(url='/account')),
    url(r'^blog/', include('blog.urls', namespace='blog')),
    url(r'^admin/', admin.site.urls),
]


if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
