from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager
)
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.template.loader import get_template
from django.conf import settings
from my_korea.utils import unique_key_activation_generator
from django.db.models.signals import pre_save, post_save
from django.utils import timezone
DEFAULT_ACTIVATION_DAYS = 7


class UserManager(BaseUserManager):
    def create_user(self, email, full_name, phone_number, password=None, is_active=True, is_staff=False, is_admin=False):
        if not email:
            raise ValueError("У пользователя должен быть email!")
        if not password:
            raise ValueError("У пользователя должен быть пароль!")
        if not full_name:
            raise ValueError("Вы должны указать имя и фамилию!")
        if not phone_number:
            raise ValueError("Укажите номер телефона!")
        user_object = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            phone_number=phone_number,
        )
        user_object.set_password(password)
        user_object.staff = is_staff
        user_object.admin = is_admin
        user_object.active = is_active
        user_object.save(using=self._db)
        return user_object

    def create_staff_user(self, email, full_name, phone_number, password=None):
        user = self.create_user(
            email,
            full_name,
            phone_number,
            password=password,
            is_staff=True
        )
        return user

    def create_superuser(self, email, full_name, phone_number, password=None):
        user = self.create_user(
            email,
            full_name,
            phone_number,
            password=password,
            is_staff=True,
            is_admin=True
        )
        return user


class User(AbstractBaseUser):
    email = models.EmailField(unique=True, max_length=255)
    full_name = models.CharField(max_length=50, blank=True, null=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,12}$',
                                 message="Введите телефон в следующем формате: '+999999999'.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    REQUIRED_FIELDS = ['full_name', 'phone_number']

    def __str__(self):
        return self.email

    def get_full_name(self):
        if self.full_name:
            return self.full_name
        return self.email

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, object=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active


class EmailActivationQuerySet(models.query.QuerySet):
    def confirmable(self):
        now = timezone.now()
        start_range = now - timezone.timedelta(days=DEFAULT_ACTIVATION_DAYS)
        end_range = now
        return self.filter(
            activated=False,
            forced_expired=False
        ).filter(
            timestamp__gt=start_range,
            timestamp__lte=end_range
        )


class EmailActivationManager(models.Manager):
    def get_queryset(self):
        return EmailActivationQuerySet(self.model, using=self._db)

    def confirmable(self):
        return self.get_queryset().confirmable()

    def email_exists(self, email):
            return self.get_queryset().filter(
                Q(email=email) |
                Q(user__email=email)
            ).filter(
                activated=False
            )


class EmailActivation(models.Model):
    user = models.ForeignKey(User)
    email = models.EmailField()
    key = models.CharField(max_length=120, blank=True, null=True)
    activated = models.BooleanField(default=False)
    forced_expired = models.BooleanField(default=False)
    expires = models.IntegerField(default=7)  # 7 дней
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    objects = EmailActivationManager()

    def __str__(self):
        return self.email

    def can_activate(self):
        qs = EmailActivation.objects.filter(pk=self.pk).confirmable()
        if qs.exists():
            return True
        return False

    def activate(self):
        if self.can_activate():
            user = self.user
            user.active = True
            user.save()
            self.activated = True
            self.save()
            return True
        return False

    def regenerate(self):
        self.key = None
        self.save()
        if self.key is not None:
            return True
        return False

    def send_activation_email(self):
        if not self.activated and not self.forced_expired:
            if self.key:
                base_url = getattr(settings, 'BASE_URL', 'https://www.mykoreabeauty.com.ua')
                key_path = reverse("account:email-activate", kwargs={'key': self.key})
                path = "{base}{path}".format(base=base_url, path=key_path)
                context = {
                    'path': path,
                    'email': self.email
                }
                txt_ = get_template('registration/emails/verify.txt').render(context)
                html_ = get_template('registration/emails/verify.html').render(context)
                subject = 'Активация Учетной записи'
                sent_mail = send_mail(
                    subject,
                    message=txt_,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[self.email],
                    html_message=html_,
                    fail_silently=False,
                )
                return sent_mail
        return False


def pre_save_email_activation(sender, instance, *args, **kwargs):
    if not instance.activated and not instance.forced_expired:
        if not instance.key:
            instance.key = unique_key_activation_generator(instance)


pre_save.connect(pre_save_email_activation, sender=EmailActivation)


def post_save_user_create_receiver(sender, instance, created, *args, **kwargs):
    if created:
        obj = EmailActivation.objects.create(user=instance, email=instance.email)
        obj.send_activation_email()


post_save.connect(post_save_user_create_receiver, sender=User)


class GuestEmail(models.Model):
    email        = models.EmailField()
    phone        = models.CharField( max_length=17, blank=True)
    active       = models.BooleanField(default=True)
    timestamp    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
