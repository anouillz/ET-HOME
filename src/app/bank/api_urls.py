from django.urls import path
from . import views

urlpatterns = [
    path('clients/add', views.add_client, name='add_client'),
    path('categories/add', views.add_category, name='add_category'),
    path('accounts/add', views.add_account, name='add_account'),
    path('accounts/<uuid:id>/delete', views.delete_account, name='delete_account'),
    path('accounts/<uuid:id>/edit', views.edit_account, name='edit_account'),
    path('transactions/add', views.add_transaction, name='add_transaction'),
    path('transactions/<uuid:id>/edit', views.edit_transaction, name='edit_transaction'),
    path('transactions/<uuid:id>/delete', views.delete_transaction, name='delete_transaction'),
    path("transactions/get",views.filter_transaction,name="filter_transactions"),
    path("transactions/<uuid:id>",views.get_transaction,name="get_transaction"),
    path("auth/secret", views.generate_secret, name="gen_secret"),
    path("auth/token", views.generate_token, name="gen_token")
]
