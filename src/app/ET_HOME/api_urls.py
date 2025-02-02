from django.urls import path

from ET_HOME import api_views

app_name = "api"

urlpatterns = [
    path("", api_views.api_access, name="doc"),

    path("user/change_password/", api_views.change_password, name="change_password"),
    path("user/totp/", api_views.activate_totp, name="activate_totp"),
    path("user/login/", api_views.user_login, name="login"),
    path("user/", api_views.modify_user, name="modify_user"),

    # Accounts
    path("accounts/<uuid:id>/transactions/<date:first_date>/<date:second_date>/", api_views.get_account_transactions, name="get_account_transactions"),
    path("accounts/<uuid:id>/", api_views.AccountAPI.as_view(), name="account_api"),
    path("accounts/<str:account_number>/sync/<date:from_date>/", api_views.sync_account, name="sync_account_from"),
    path("accounts/<str:account_number>/sync/", api_views.sync_account, name="sync_account"),
    path("accounts/", api_views.accounts_api, name="accounts_api"),

    # Transactions
    path("transactions/<date:first_date>/<date:second_date>/", api_views.get_transactions, name="get_transactions"),
    path("transactions/<uuid:id>/", api_views.TransactionAPI.as_view(), name="transaction_api"),
    path("transactions/cash/<date:first_date>/<date:second_date>/", api_views.get_cash_transactions, name="get_cash_transactions"),
    path("transactions/cash/", api_views.get_cash_transactions, name="get_cash_transactions"),
    path("transactions/", api_views.add_transaction, name="add_transactions"),
    path("outcomes/<date:first_date>/<date:second_date>/", api_views.get_outcomes, name="get_outcomes"),
    path("incomes/<date:first_date>/<date:second_date>/", api_views.get_incomes, name="get_incomes"),

    # Categories
    path("categories/<uuid:id>/", api_views.CategoryAPI.as_view(), name="category_api"),
    path("categories/", api_views.categories_api, name="categories_api"),
    path("categories/update", api_views.update_categories, name="update_categories"),
    path("accounts/", api_views.accounts_api, name="accounts_api"),

    # Misc
    path("test_secret/", api_views.test_secret, name="test_secret"),
    path("export/", api_views.export_data, name="export_data"),
    path("notifications/",api_views.get_notifications, name="get_notifications"),
    path("notifications/<uuid:id>/read/",api_views.read_notification, name="read_notification"),
    path("sync/<date:from_date>/", api_views.sync_user, name="sync_user_from"),
    path("sync/", api_views.sync_user, name="sync_user")
]