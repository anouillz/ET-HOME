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
    path("login/", views.login_view,name="login"),
    path("register/", views.register_view,name="register"),
    path("", views.dashboard_view,name="dashboard"),
    path("bank/", include("bank.urls", namespace="bank")),

    #Dashboard
    path("addAccount/", views.add_account_view, name="add_bank"),
    path("account/", views.account_view, name="account"),
    path("settings/", views.settings_view, name="settings"),
    path("logout/", views.logout_view, name="logout"),
    path("categories/", views.categories_view, name="categories"),
    path("transactions/", views.transactions_view, name="transactions"),



    #Application API
    path("api/", views.api_access, name="api"),
    path("api/accounts/<uuid:id>/transactions/<date:first_date>/<date:second_date>/", views.get_account_transactions, name="get_account_transactions"),
    path("api/accounts/<uuid:id>/", views.get_account, name="get_account"),
    path("api/transactions/<date:first_date>/<date:second_date>/", views.get_transactions, name="get_transactions"),
    path("api/transactions/", views.add_transaction, name="add_transactions"),
    path("api/outcomes/<date:first_date>/<date:second_date>/", views.get_outcomes, name="get_outcomes"),
    path("api/incomes/<date:first_date>/<date:second_date>/", views.get_incomes, name="get_incomes"),
    path("api/categories/<uuid:id>/", views.category, name="category"),
    path("api/categories/", views.categories, name="categories"),
    path("api/accounts/", views.get_accounts, name="get_accounts"),
    path("api/add_bank_account/", views.add_bank_account, name="add_bank_account"),
    path("api/test_secret", views.test_secret, name="test_secret"),
    path("api/export/", views.export_data, name="export_data"),
    path("api/notifications/",views.get_notifications, name="get_notifications"),
    path("api/notifications/<uuid:id>/read/",views.read_notification, name="read_notification"),
    path("api/accounts/<str:account_number>/sync/<date:from_date>", views.sync_account, name="sync_account_from"),
    path("api/accounts/<str:account_number>/sync/", views.sync_account, name="sync_account"),
    path("api/sync/<date:from_date>/", views.sync_user, name="sync_user_from"),
    path("api/sync/", views.sync_user, name="sync_user"),

    #Categories page
    path("categories/add/", views.add_category, name="add_category"),
    path("categories/delete/", views.delete_category, name="delete_category"),
    path("categories/update_budget/", views.update_category_budget, name="update_category_budget")

]
