from django.db import models
from billing.models import BillingProfile

ADDRESS_TYPES = (
    ('billing', 'Billing'),
    ('shipping', 'Shipping'),
                )


class Address(models.Model):
    billing_profile = models.ForeignKey(BillingProfile)
    address_type    = models.CharField(max_length=120, choices=ADDRESS_TYPES)
    address_line_1  = models.CharField(max_length=120)
    address_line_2  = models.CharField(max_length=120, null=True, blank=True)
    city            = models.CharField(max_length=120)
    street          = models.CharField(max_length=120)
    otdelenie_NP    = models.CharField(max_length=120)
    zip_code        = models.CharField(max_length=120)

    def __str__(self):
        return str(self.billing_profile)

    def get_address(self):
        return "{city},\n{street},\n Отделение Новой Почты: {otdelenie_NP},\n{zip_code}".format(
            city=self.city,
            street=self.street,
            otdelenie_NP=self.otdelenie_NP,
            zip_code=self.zip_code
        )
