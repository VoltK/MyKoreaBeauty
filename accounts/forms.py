from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import EmailActivation
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.contrib import messages


User = get_user_model()


class ReactivateEmailForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ваш email',
    }))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = EmailActivation.objects.email_exists(email)
        if not qs.exists():
            register_url = reverse("register")
            msg = """"Этого email несуществует.
                            Вы хотите <a href="{link}">зарегистрироваться</a>?
                            """.format(link=register_url)
            return forms.ValidationError(mark_safe(msg))
        return email


class UserDetailChangeForm(forms.ModelForm):
    full_name = forms.CharField(label="Имя", required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Вашe имя',
    }))
    phone_number = forms.CharField(label="Телефон", required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ваш телефонный номер',
    }))


    class Meta:
        model = User
        fields = ['full_name', 'phone_number']


class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone_number') #'full_name',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone_number', 'password', 'active', 'admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class RegisterForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ваш email',
    }))
    full_name = forms.CharField(label='Имя', widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Ваше имя'}))
    phone_number = forms.CharField(label='Телефон', widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Ваше контактный номер'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Ваш пароль'}))
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Ваш пароль'}))

    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone_number')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.active = False  # письмо подтвержение будет отправлено Джанго сигналами
        #obj = EmailActivation.objects.create(user=user)
        #obj.send_activation_email()
        if commit:
            user.save()
        return user


class GuestForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ваш email',
    }))
    phone = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите номер телефона в формате:+380.... ',
    }))


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ваш email',
        'style': 'margin-left: 10px',
    }))

    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ваш пароль',
        'style': 'margin-left: 10px',
    }))

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        request = self.request
        data = self.cleaned_data
        email = data.get('email')
        password = data.get('password')
        qs = User.objects.filter(email=email)
        if qs.exists():
            not_active = qs.filter(active=False)
            if not_active.exists():
                link = reverse('account:resend-activation')
                reconfirm_msg = """<a href='{resend_link}'> Перейдите сюда для повторной отправки активационного email</a>
                """.format(resend_link=link)
                email_activation = EmailActivation.objects.filter(email=email)
                is_conf = email_activation.confirmable().exists()
                if is_conf:
                    msg1 = "Проверьте свою почту для активации аккаунта или" + reconfirm_msg.lower()
                    raise forms.ValidationError(mark_safe(msg1))
                email_conf_qs = EmailActivation.objects.email_exists(email)
                if email_conf_qs.exists():
                    raise forms.ValidationError(mark_safe('Email неподтверден.' + reconfirm_msg))
                if not is_conf and not email_conf_qs.exists():
                    raise forms.ValidationError('Этот аккаунт неактивирован')

        user = authenticate(request, username=email, password=password)
        if user is None:
            raise forms.ValidationError('Неправильный логин или пароль')
        login(request, user)
        self.user = user
        return data
