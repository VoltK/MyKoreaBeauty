from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import LoginForm, RegisterForm, GuestForm, ReactivateEmailForm, UserDetailChangeForm
from django.views.generic.edit import FormMixin
from django.views.generic import CreateView, FormView, DetailView, View, UpdateView
from .models import GuestEmail, EmailActivation
from django.utils.http import is_safe_url
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

# Функцией
# @login_required
# def acc_home(request):
#     return render(request, "accounts/home.html")


# Классом
class AccountHomeView(LoginRequiredMixin, DetailView):
    template_name = 'accounts/home.html'

    def get_object(self):
        return self.request.user

    # тоже самое, что и LoginRequiredMixin
    # @method_decorator(login_required)
    # def dispatch(self, request, *args, **kwargs):
    #     return super(AccountHomeView, self).dispatch(self, *args, **kwargs)


class AccountEmailActivationView(FormMixin, View):
    success_url = '/login/'
    form_class = ReactivateEmailForm
    key = None

    def get(self, request, key=None, *args, **kwargs):
        self.key = key
        if key is not None:
            qs = EmailActivation.objects.filter(key__iexact=key)
            confirm_qs = qs.confirmable()
            if confirm_qs.count() == 1:
                obj = confirm_qs.first()
                obj.activate()
                messages.success(request, 'Вы успешно подтвердили email и теперь можете войти.')
                return redirect('login')
            else:
                activated_qs = qs.filter(activated=True)
                if activated_qs.exists():
                    reset_url = reverse('password_reset')
                    msg = """Вы уже подтвердили ваш email.
                    Вы хотите <a href="{link}">сменить пароль</a>?
                    """.format(link=reset_url)
                    messages.success(request, mark_safe(msg))
                    return redirect('login')
        context = {'form': self.get_form(), 'key': key}
        return render(request, 'registration/activation-error.html', context)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        msg = """Ссылка для активации отправлена. Пожалуйста, проверьте свою почту"""
        request = self.request
        messages.success(request, msg)
        email = form.cleaned_data.get("email")
        obj = EmailActivation.objects.email_exists(email).first()
        user = obj.user
        new_activation = EmailActivation.objects.create(user=user, email=email)
        new_activation.send_activation_email()
        return super(AccountEmailActivationView, self).form_valid(form)

    def form_invalid(self, form):
        context = {'form': form, 'key': self.key}
        return render(self.request, 'registration/activation-error.html', context)


class NextUrlMixin(object):
    default_next = "/"

    def get_next_url(self):
        request = self.request
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        if is_safe_url(redirect_path, request.get_host()):
                return redirect_path
        return self.default_next


class GuestRegisterView(NextUrlMixin, FormView):
    form_class = GuestForm
    default_next = '/register/'

    def form_invalid(self, form):
        return redirect(self.default_next)

    def form_valid(self, form):
        phone = form.cleaned_data.get('phone')
        email = form.cleaned_data.get('email')
        new_guest_phone_email = GuestEmail.objects.create(phone=phone, email=email)
        self.request.session['guest_phone_email_id'] = new_guest_phone_email.id
        return redirect(self.get_next_url())


class LoginView(FormView):
    form_class = LoginForm
    success_url = 'product:list'
    template_name = 'auth/login.html'

    def get_form_kwargs(self):
        kwargs = super(LoginView, self).get_form_kwargs()
        print(kwargs)
        kwargs['request'] = self.request
        return kwargs

    def get_next_url(self):
        request = self.request
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        if is_safe_url(redirect_path, request.get_host()):
            return redirect_path
        else:
            return 'product:list'

    def form_valid(self, form):
            next_path = self.get_next_url()
            return redirect(next_path)


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "auth/register.html"
    success_url = '/login/'


class UserDetailUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserDetailChangeForm
    template_name = 'accounts/form_user_detail_update.html'

    def get_object(self):
        return self.request.user

    def get_context_data(self, *args, **kwargs):
        context = super(UserDetailUpdateView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Изменить ваши данные'
        return context

    def get_success_url(self):
        return reverse('account:home')

