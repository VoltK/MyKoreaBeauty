from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View
from .utils import Mailchimp
from .models import MarketingPreference
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
MAILCHIMP_EMAIL_LIST_ID = getattr(settings, "MAILCHIMP_EMAIL_LIST_ID", None)


class CsrfExemptMixin(object):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CsrfExemptMixin, self).dispatch(request, *args, **kwargs)


class MailchimpWebhookView(CsrfExemptMixin, View):
    def post(self, request, *args, **kwargs):
        data = request.POST
        list_id = data.get('data[list_id]')
        if str(list_id) == str(MAILCHIMP_EMAIL_LIST_ID):
            email = data.get('data[email]')
            hook_type = data.get('type')
            response_status, response = Mailchimp().check_subcription_status(email)
            subscription_status = response['status']
            if subscription_status == 'subscribed':
                qs = MarketingPreference.objects.filter(user__email__iexact=email)
                if qs.exists():
                    qs.update(subscribed=True, mailchimp_subscribed=True, mailchimp_msg=str(data))
            if subscription_status == 'unsubscribed':
                qs = MarketingPreference.objects.filter(user__email__iexact=email)
                if qs.exists():
                    qs.update(subscribed=False, mailchimp_subscribed=False, mailchimp_msg=str(data))

        return HttpResponse('Спасибо', status=200)
