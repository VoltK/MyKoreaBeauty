from django.contrib import admin
from .models import ObjectView, UserSession

admin.site.register(ObjectView)

admin.site.register(UserSession)
