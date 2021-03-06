import random
import os
from django.db.models import Q
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.urls import reverse
from my_korea.utils import unique_slug_generator


def get_filename_ext(filepath):
        base_name = os.path.basename(filepath)
        name, ext = os.path.splitext(base_name)
        return name, ext


def upload_image_path(instance, filename):
    #print(instance)
    #print(filename)
    new_filename = random.randint(1, 55555555555555)
    name, ext = get_filename_ext(filename)
    final_filename = f'{new_filename}{ext}'
    return "products/{new_filename}/{final_filename}".format(
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
        return reverse('product:list_by_category', args=[self.slug])


class ProductQuerySet(models.query.QuerySet):

    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True, active=True)

    def search(self, query):
            lookups = (Q(title__icontains=query) |
                       Q(description__icontains=query) |
                       Q(tag__title__icontains=query))
            return self.filter(lookups).distinct()


class ProductManager(models.Manager):

    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def featured(self):  # Product.objects.featured()
        return self.get_queryset().featured()

    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id)
        if qs.count() == 1:
            return qs.first()
        return None

    def search(self, query):
        return self.get_queryset().active().search(query)


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, blank=True, null=True)
    title       = models.CharField(max_length=120)
    slug        = models.SlugField(blank=True, unique=True)
    description = models.TextField(null=True)
    price       = models.DecimalField(max_digits=20, decimal_places=2, default=49.99)
    sale_price  = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    image       = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    active      = models.BooleanField(default=True)
    timestamp   = models.DateTimeField(auto_now_add=True)
    status      = models.CharField(max_length=120, blank=True, null=True)

    objects = ProductManager()

    class Meta:
        ordering = ('title',)
        index_together = (('id', 'slug'),)
        verbose_name = 'продукт'
        verbose_name_plural = 'продукты'

    def get_absolute_url(self):
        #return "/products/{slug}/".format(slug=self.slug)
        return reverse('product:detail', args=[self.id, self.slug])

    def __str__(self):
        return self.title


def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(product_pre_save_receiver, sender=Product)


def category_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(category_pre_save_receiver, sender=Category)
