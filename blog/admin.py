from django.contrib import admin
from .models import Post, Category
# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'slug', 'id']
    search_fields = ['name']

    class Meta:
        model = Category


admin.site.register(Category, CategoryAdmin)


admin.site.register(Post)
