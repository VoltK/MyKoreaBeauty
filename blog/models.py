import random
import os
from django.db import models
from django.urls import reverse
from django.db.models.signals import pre_save, post_save
from my_korea.utils import unique_slug_generator


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    # print(instance)
    # print(filename)
    new_filename = random.randint(1, 55555555555555)
    name, ext = get_filename_ext(filename)
    final_filename = f'{new_filename}{ext}'
    return "posts/{new_filename}/{final_filename}".format(
        new_filename=new_filename,
        final_filename=final_filename
    )


class Category(models.Model):
    title = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('title',)
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:list_post_by_category', args=[self.slug])




class Post(models.Model):
    category = models.ForeignKey(Category, related_name='posts', on_delete=models.CASCADE, blank=True, null=True)
    title       = models.CharField(max_length=120)
    picture     = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    information = models.TextField(blank=True, null=True)
    timestamp   = models.DateTimeField(auto_now_add=True)
    slug        = models.SlugField(blank=True, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('title',)
        index_together = (('id', 'slug'),)
        verbose_name = 'пост'
        verbose_name_plural = 'Посты'

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.id, self.slug])


def post_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(post_pre_save_receiver, sender=Post)


def category_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(category_pre_save_receiver, sender=Category)
