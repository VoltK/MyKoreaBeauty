from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.views.generic import ListView, DetailView
from .models import Post, Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def post_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    posts = Post.objects.all()
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        posts = Post.objects.filter(category=category)

    # pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(posts, 3)

    try:
        pag_post = paginator.page(page)
    except PageNotAnInteger:
        pag_post = paginator.page(1)
    except EmptyPage:
        pag_post = paginator.page(paginator.num_pages)
    # конец pagination

    context = {
        'category': category,
        'categories': categories,
        'posts': pag_post,
    }
    return render(request, 'post/post_list.html', context)


class PostListView(ListView):
    template_name = 'post/post_list.html'
    paginate_by = 3

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Post.objects.all()


class PostDetailView(DetailView):
    template_name = 'post/post_detail.html'
    queryset = Post.objects.all()

    def get_object(self, *args, **kwargs):
        request = self.request
        slug = self.kwargs.get('slug')
        try:
            instance = Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            raise Http404("Ничего не найдено")
        except Post.MultipleObjectsReturned:
            qs = Post.objects.filter(slug=slug)
            instance = qs.first()
        except:
            raise Http404('Произошла ошибка')
        return instance