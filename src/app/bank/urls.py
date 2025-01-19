from django.urls import path, include
from . import views

urlpatterns = [
    path("api/", include("bank.api_urls")),
    path("add_account", views.add_account_view, name='add_account'),
]
