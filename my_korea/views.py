from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .forms import ContactForm


def home_page(request):
    context = {"title": "Index page",
               "content": "Here is our home page. We are in process"}

    if request.user.is_authenticated():
        context['premium_content'] = "Here is our products for VIP"
    return render(request, "home_page.html", context)


def about_page(request):
    context = {
        "title": "About Page",
        "content": " Welcome to the about page."
    }
    return render(request, "home_page.html", context)


def contact_page(request):
        contact_form = ContactForm(request.POST or None)
        context = {
            "title": "Contact",
            "content": " Welcome to the contact page.",
            "form": contact_form,
        }
        if contact_form.is_valid():
            print(contact_form.cleaned_data)
            if request.is_ajax():
                return JsonResponse({"message": "Thank you"})

        if contact_form.errors:
            print(contact_form.cleaned_data)
            errors = contact_form.errors.as_json()
            if request.is_ajax():
                return HttpResponse(errors, status=400, content_type='application/json')

        return render(request, 'contact.html', context)




