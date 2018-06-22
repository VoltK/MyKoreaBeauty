from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager
)


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


class Profile(models.Model):
    user = models.OneToOneField(User)


class GuestEmail(models.Model):
    email        = models.EmailField()
    phone        = models.CharField( max_length=17, blank=True)
    active       = models.BooleanField(default=True)
    timestamp    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
