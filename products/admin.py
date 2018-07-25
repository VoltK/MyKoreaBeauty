from django.contrib import admin
from .models import Product, Category
# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'slug', 'id']
    search_fields = ['name']

    class Meta:
        model = Category


admin.site.register(Category, CategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'price', 'category', "slug", 'id']
    search_fields = ['title', 'category']

    class Meta:
        model = Product


admin.site.register(Product, ProductAdmin)
