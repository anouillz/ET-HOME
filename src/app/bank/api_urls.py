from django.urls import path
from . import views

urlpatterns = [
    path('accounts/add', views.add_account, name='add_account'),
    path('transactions/add', views.add_transaction, name='add_transaction'),
    path("transactions/<str:id>",views.get_transaction,name="get_transaction"),
    path("transactions/get",views.filter_transaction,name="filter_transactions"),
    path("auth/secret", views.generate_secret, name="gen_secret"),
    path("auth/token", views.generate_token, name="gen_token"),
]
