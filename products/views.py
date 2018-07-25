from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from cart.models import Cart
from analytics.mixins import ObjectViewedMixin
from .models import Product, Category
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.all()
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category)

    # pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(products, 6)

    try:
        pag_prod = paginator.page(page)
    except PageNotAnInteger:
        pag_prod = paginator.page(1)
    except EmptyPage:
        pag_prod = paginator.page(paginator.num_pages)
    # конец pagination

    # корзина
    cart_object, new_object = Cart.objects.new_or_get(request)

    context = {
        'category': category,
        'categories': categories,
        'products': pag_prod,
        'cart': cart_object
    }
    return render(request, 'products/list.html', context)

# не знаю как заставить сортировать по категориям используя классы
class ProductListView(ListView):
    template_name = 'products/list.html'
    paginate_by = 6

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView, self).get_context_data(*args, **kwargs)
        cart_object, new_object = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_object
        #тестовая часть для добавления категорий
        # category = None
        # categories = Category.objects.all()
        # products = self.get_queryset()
        # if category_slug:
        #     category = get_object_or_404(Category, slug=category_slug)
        #     products = Product.objects.filter(category=category)
        # context['category'] = category
        # context['categories'] = categories
        # context['products'] = products
        return context

    #Вызывать эту функцию нужно только когда хочешь добавить новую инфу в модель
    # def get_context_data(self, *args, **kwargs):
    #     context = super(ProductListView, self).get_context_data(*args, **kwargs)
    #     return context


class ProductDetailView(ObjectViewedMixin, DetailView):
    queryset = Product.objects.all()
    template_name = 'products/details.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        cart_object, new_object = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_object
        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        slug = self.kwargs.get('slug')
        try:
            instance = Product.objects.get(slug=slug, active=True)
        except Product.DoesNotExist:
            raise Http404("Ничего не найдено")
        except Product.MultipleObjectsReturned:
            qs = Product.objects.filter(slug=slug, active=True)
            instance = qs.first()
        except:
            raise Http404('Произошла ошибка')
        return instance


class UserHistoryProductView(LoginRequiredMixin, ListView):
    template_name = 'products/user_history.html'

    def get_queryset(self, *args, **kwargs):
        request = self.request
        views = request.user.objectview_set.by_model(Product)
        #viewed_ids = [x.object_id for x in views]
        return views

    def get_context_data(self, *args, **kwargs):
        context = super(UserHistoryProductView, self).get_context_data(*args, **kwargs)
        cart_object, new_object = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_object
        return context

