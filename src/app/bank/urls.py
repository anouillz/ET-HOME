from django.urls import path
from . import views

urlpatterns = [
    path('client/me/', views.get_client, name='get_client'),
]