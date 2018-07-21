from django import forms
from .models import Address


class AddressForm(forms.ModelForm):
    city = forms.CharField(label='Город', widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))

    street = forms.CharField(label='Улица', widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))

    otdelenie_NP = forms.CharField(label='Отделение Новой Почты', widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    zip_code = forms.CharField(label='Почтовый индекс', widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    class Meta:
        model = Address
        fields = [#'billing_profile',
                  'city',
                  'street',
                  'otdelenie_NP',
                  'zip_code']
