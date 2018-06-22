from django.contrib import admin
from .models import MarketingPreference
# Register your models here.


class MarketingPrefAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscribed', 'update']
    readonly_fields = ['mailchimp_subscribed', 'mailchimp_msg', 'timestamp', 'update']

    class Meta:
        model = MarketingPreference
        fields = ['user',
                  'subscribed',
                  'mailchimp_subscribed',
                  'mailchimp_msg',
                  'timestamp',
                  'update'
                  ]


admin.site.register(MarketingPreference, MarketingPrefAdmin)

