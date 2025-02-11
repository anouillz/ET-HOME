from django.urls import path, include
from . import views

app_name = "bank"
urlpatterns = [
    path("api/", include("bank.api_urls")),
    path("", views.home_view, name="home"),
    path("add_client/", views.add_client_view, name="add_client"),
    path("add_account/", views.add_account_view, name="add_account"),
    path("add_transaction/", views.add_transaction_view, name="add_transaction"),
    path("add_category/", views.add_category_view, name="add_category"),
    path("clients/", views.clients_view, name="clients"),
    path("accounts/<uuid:id>/", views.edit_account_view, name="edit_account"),
    path("accounts/", views.accounts_view, name="accounts"),
    path("transactions/<uuid:id>/", views.edit_transaction_view, name="edit_transaction"),
    path("transactions/", views.transactions_view, name="transactions"),
]
