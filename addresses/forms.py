from django import forms
from .models import Address


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [#'billing_profile',
                  'city',
                  'street',
                  'otdelenie_NP',
                  'zip_code']
