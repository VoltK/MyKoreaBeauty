from django.contrib import admin
from .models import Address


class AddressAdmin(admin.ModelAdmin):
    list_display = ['__str__', "city", 'id']

    class Meta:
        model = Address


admin.site.register(Address, AddressAdmin)
