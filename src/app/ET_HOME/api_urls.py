from django.urls import path

from ET_HOME import api_views

app_name = "api"

urlpatterns = [
    path("", api_views.api_access, name="doc"),
    path("accounts/<uuid:id>/transactions/<date:first_date>/<date:second_date>/", api_views.get_account_transactions, name="get_account_transactions"),
    path("accounts/<uuid:id>/", api_views.get_account, name="get_account"),
    path("transactions/<date:first_date>/<date:second_date>/", api_views.get_transactions, name="get_transactions"),
    path("transactions/", api_views.add_transaction, name="add_transactions"),
    path("outcomes/<date:first_date>/<date:second_date>/", api_views.get_outcomes, name="get_outcomes"),
    path("incomes/<date:first_date>/<date:second_date>/", api_views.get_incomes, name="get_incomes"),
    path("categories/<uuid:id>/", api_views.CategoryAPI.as_view(), name="category_api"),
    path("categories/", api_views.categories_api, name="categories_api"),
    path("accounts/", api_views.accounts_api, name="accounts_api"),
    path("test_secret", api_views.test_secret, name="test_secret"),
    path("export/", api_views.export_data, name="export_data"),
    path("notifications/",api_views.get_notifications, name="get_notifications"),
    path("notifications/<uuid:id>/read/",api_views.read_notification, name="read_notification"),
    path("accounts/<str:account_number>/sync/<date:from_date>", api_views.sync_account, name="sync_account_from"),
    path("accounts/<str:account_number>/sync/", api_views.sync_account, name="sync_account"),
    path("sync/<date:from_date>/", api_views.sync_user, name="sync_user_from"),
    path("sync/", api_views.sync_user, name="sync_user")
]