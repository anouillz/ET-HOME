def navbar_links(request):
    return {
        "nav_links": [
            {'url_name': 'dashboard', 'label': 'Dashboard'},
            {'url_name': 'categories', 'label': 'Categories'},
            {'url_name': 'add_bank', 'label': 'Add bank account'},
            {'url_name': 'settings', 'label': 'Settings'}
        ],
        "bank_nav_links": [
            {'url_name': 'bank:add_account', 'label': 'Add account'},
            {'url_name': 'bank:add_transaction', 'label': 'Add transaction'},
            {'url_name': 'bank:add_category', 'label': 'Add category'},
            {'url_name': 'bank:accounts', 'label': 'Accounts'},
            {'url_name': 'bank:transactions', 'label': 'Transactions'},
        ]
    }