from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
import json
from .models import Client, BankAccount, Transaction, SpendingCategory

# Get client by ID
def get_client_from_id(request, id):
    if request.method == 'GET':
        client = get_object_or_404(Client, id=id)
        client_data = {
            'id': client.id,
            'firstname': client.first_name,
            'lastname': client.last_name,
            'accounts': [
                {
                    'id': str(account.id),
                    'balance': float(account.balance),
                    'bank_name': account.bank_name,
                    'transactions': [
                        {
                            'id': str(transaction.id),
                            'amount': float(transaction.amount),
                            'description': transaction.description,
                            'category': transaction.category.name if transaction.category else None,
                            'date': transaction.date
                        }
                        for transaction in account.transaction_set.all()
                    ]
                }
                for account in client.bank_accounts.all()
            ]
        }

        return JsonResponse({'client': client_data})

    return JsonResponse({'error': 'Invalid request method'}, status=405)
def search_client(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            firstname = data.get('firstname')
            lastname = data.get('lastname')
            if not firstname or not lastname:
                return JsonResponse({'error': 'Both firstname and lastname are required'}, status=400)
            client = get_object_or_404(Client, first_name=firstname, last_name=lastname)
            
            client_data = {
                'id': client.id,
                'firstname': client.first_name,
                'lastname': client.last_name,
                'accounts': [
                    {
                        'id': str(account.id),
                        'balance': float(account.balance),
                        'bank_name': account.bank_name,
                        'transactions': [
                            {
                                'id': str(transaction.id),
                                'amount': float(transaction.amount),
                                'description': transaction.description,
                                'category': transaction.category.name if transaction.category else None,
                                'date': transaction.date
                            }
                            for transaction in account.transaction_set.all()
                        ]
                    }
                    for account in client.bank_accounts.all()
                ]
            }

            return JsonResponse({'client': client_data})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
