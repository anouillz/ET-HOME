from django.urls import path
from . import views

urlpatterns = [
    path('client/me/', views.get_client, name='get_client'),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('add_account/', views.add_account, name='add_account')
]
