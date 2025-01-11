from django.urls import path
from . import views

urlpatterns = [
    path('client/<str:id>/', views.get_client_from_id, name='get_client'),
    path('client/search/',views.search_client,name='search_client')
]