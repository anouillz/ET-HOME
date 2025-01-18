from django.urls import path
from . import views

urlpatterns = [
    path('client/me/', views.get_client, name='get_client'),
    path('transactions/add', views.add_transaction, name='add_transaction'),
    path('accounts/add', views.add_account, name='add_account'),
    path("transactions/<str:id>",views.get_transaction,name="get_transaction"),
    path("transactions/filter",views.filter_transaction,name="filter_transactions"),
    path("transactions/all",views.get_all_transaction,name="get_all_transactions"),
]
