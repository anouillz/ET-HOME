from django.urls import path, include
from . import views

app_name = "bank"
urlpatterns = [
    path("api/", include("bank.api_urls")),
    path("add_account", views.add_account_view, name='add_account'),
    path("add_transaction", views.add_transaction_view, name='add_transaction'),
    path("add_category", views.add_category_view, name='add_category'),
    path("accounts", views.accounts_view, name='accounts'),
    path("transactions", views.transactions_view, name='transactions'),
]
