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
from django.urls import path, include, register_converter
from . import views
from .converters import DateConverter

register_converter(DateConverter, "date")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/",views.login_view,name="login"),
    path("register/",views.register_view,name="register"),
    path("",views.dashboard_view,name="dashboard"),
    path("bank/", include("bank.urls", namespace="bank")),

    #Dashboard
    path("addAccount/", views.add_account_view, name="add_bank"),
    path("account/", views.account_view, name="account"),
    path("settings/", views.settings_view, name="settings"),
    path("logout/", views.logout_view, name="logout"),
    path("categories/", views.category_view, name="categories"),

    #Application API
    path("api/", views.api_access, name="api"),
    path("api/accounts/<uuid:id>/transactions/<date:first_date>/<date:second_date>/", views.get_account_transactions, name="get_account_transactions"),
    path("api/transactions/<date:first_date>/<date:second_date>/", views.get_transactions, name="get_transactions"),
    path("api/get_outcomes/<date:first_date>/<date:second_date>/", views.get_outcomes, name="get_outcomes"),
    path("api/get_incomes/<date:first_date>/<date:second_date>/", views.get_incomes, name="get_incomes"),
    path("api/get_bankAccount_info/<uuid:id>/", views.get_bankAccount_info, name="get_bankAccount_info"),
    path("api/categories/", views.get_categories, name="get_categories"),
    path("api/get_category/<uuid:id>/", views.get_category, name="get_category"),
    path("api/get_accounts/", views.get_accounts, name="get_accounts"),
    path("api/add_transaction/", views.add_transactions, name="add_transactions"),
    path("api/add_bank_account", views.add_bank_account, name="add_bank_account"),
    path("api/test_secret", views.test_secret, name="test_secret"),
    path("api/export/", views.export_data, name="export_data"),
    path("api/get_notifications",views.get_notifications, name="get_notifications"),
    path("api/read_notification/<str:id>",views.read_notification, name="read_notification")
]
