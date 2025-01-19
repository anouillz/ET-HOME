def navbar_links(request):
    return {
        "nav_links": [
            {'url_name': 'dashboard', 'label': 'Dashboard'},
            {'url_name': 'categories', 'label': 'Categories'},
            {'url_name': 'add_bank', 'label': 'Add bank account'},
            {'url_name': 'settings', 'label': 'Settings'}
        ]
    }