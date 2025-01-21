from django.contrib import admin
from .models import SpendingCategory

@admin.register(SpendingCategory)
class SpendingCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "default_budget")
