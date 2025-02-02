from django.contrib import admin
from django.urls import path, include, register_converter, re_path
from django.views.static import serve

from . import views, settings
from .converters import DateConverter

register_converter(DateConverter, "date")

urlpatterns = [
    path("", views.dashboard_view,name="dashboard"),
    path("api/", include("ET_HOME.api_urls", namespace="api")),
    path("admin/", admin.site.urls),
    path("login/", views.login_view,name="login"),
    path("register/", views.register_view,name="register"),
    path("totp/", views.totp_setup_view,name="totp_setup"),
    path("bank/", include("bank.urls", namespace="bank")),
    path("addAccount/", views.add_account_view, name="add_bank"),
    path("settings/", views.settings_view, name="settings"),
    path("logout/", views.logout_view, name="logout"),
    path("categories/", views.categories_view, name="categories"),
    path("transactions/<uuid:id>/", views.transaction_view, name="transaction"),
    path("transactions/", views.transactions_view, name="transactions"),
    path("addTransaction/", views.add_transaction_view, name="add_transaction"),
]

if not settings.DEBUG:
    urlpatterns.append(re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings._STATIC_ROOT}))
