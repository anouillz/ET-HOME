"""
URL configuration for ET_HOME project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("login/",views.login_view,name="login"),
    path("register/",views.register_view,name="register"),
    path("",views.home_view,name="home"),
    path("bank/api/",include("bank.urls")),

    #Dashboard
    path("addBank/", views.addBank_view, name="add_bank"),
    path("account/", views.account_view, name="account"),
    path("settings/", views.settings_view, name="settings"),
    path("logout/", views.logout_view, name="logout"),
    path("categories/", views.category_view, name="categories"),

    #Application API
    path("api/", views.api_access, name="api"),
    path('api/get_transactions/<str:first_date>/<str:second_date>/', views.get_transactions, name='get_transactions'),
    path('api/get_outcomes/<str:first_date>/<str:second_date>/', views.get_outcomes, name='get_outcomes'),
    path('api/get_incomes/<str:first_date>/<str:second_date>/', views.get_incomes, name='get_incomes'),
    path('api/get_bankAccount_info/<uuid:id>/', views.get_bankAccount_info, name='get_bankAccount_info'),
    path('api/get_category/<uuid:id>/', views.get_category, name='get_category')
]
