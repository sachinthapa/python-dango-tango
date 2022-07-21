from django.contrib import admin

from . import models

# Register your models here.


class PageAdmin(admin.ModelAdmin):
    list_display = ["title", "url", "category"]


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Page, PageAdmin)
