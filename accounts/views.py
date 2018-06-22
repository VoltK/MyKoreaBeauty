from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, get_user_model
from .forms import LoginForm, RegisterForm, GuestForm
from django.views.generic import CreateView, FormView, DetailView
from .models import GuestEmail
from django.utils.http import is_safe_url
from .signals import user_logged_in

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

def guest_register(request):
    form = GuestForm(request.POST or None)
    context = {"form": form}
    print("User logged in:")
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None
    if form.is_valid():
        phone = form.cleaned_data.get('phone')
        email = form.cleaned_data.get('email')
        new_guest_phone_email = GuestEmail.objects.create(phone=phone, email=email)
        request.session['guest_phone_email_id'] = new_guest_phone_email.id
        if is_safe_url(redirect_path, request.get_host()):
            return redirect(redirect_path)
        else:
            return redirect("/register/")
    return redirect('/register/')


class LoginView(FormView):
    form_class = LoginForm
    success_url = '/products/'
    template_name = 'auth/login.html'

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        request = self.request
        user = authenticate(request, username=email, password=password)
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        if user is not None:
            login(request, user)
            user_logged_in.send(user.__class__, instance=user, request=request)
            try:
                del request.session['guest_email_id']
            except:
                pass
            if is_safe_url(redirect_path, request.get_host()):
                return redirect(redirect_path)
            else:
                return redirect("/products/")
        return super(LoginView, self).form_invalid(form)

def login_page(request):
    form = LoginForm(request.POST or None)
    context = {"form": form}
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            try:
                del request.session['guest_email_id']
            except:
                pass
            if is_safe_url(redirect_path, request.get_host()):
                return redirect(redirect_path)
            else:
                return redirect("/products/")
        else:
            print("Error")

    return render(request, "auth/login.html", context)


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "auth/register.html"
    success_url = '/login/'



# User = get_user_model()
# def register_page(request):
#     form = RegisterForm(request.POST or None)
#     context = {"form": form}
#
#     if form.is_valid():
#         form.save()
#     return render(request, "auth/register.html", context)