from django.shortcuts import render
from django.http import Http404
from django.views.generic import ListView, DetailView
from .models import Post


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