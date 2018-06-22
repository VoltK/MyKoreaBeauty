from django.conf import settings
from django.db import models
from django.db.models.signals import post_save

from accounts.models import GuestEmail
User = settings.AUTH_USER_MODEL


class BillingProfileManager(models.Manager):

    def new_or_get(self, request):
        user = request.user
        guest_info_id = request.session.get('guest_phone_email_id')
        created = False
        obj = None
        if user.is_authenticated():
            'logged in user checkout; remember payment stuff'
            obj, created = self.model.objects.get_or_create(
                user=user, email=user.email)
        elif guest_info_id is not None:
            'guest user checkout; auto reloads payment stuff'
            guest_info_obj = GuestEmail.objects.get(id=guest_info_id)
            obj, created = self.model.objects.get_or_create(
                email=guest_info_obj.email, phone=guest_info_obj.phone)
        else:
            pass

        return obj, created


class BillingProfile(models.Model):
    user      = models.OneToOneField(User, null=True, blank=True)
    email     = models.EmailField()
    phone     = models.CharField(max_length=17, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated   = models.DateTimeField(auto_now=True)
    active    = models.BooleanField(default=True)

    objects = BillingProfileManager()

    def __str__(self):
        return self.email


def user_created_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance, email=instance.email)

post_save.connect(user_created_receiver, sender=User)