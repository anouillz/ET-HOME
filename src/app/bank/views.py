import random
import string
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.http import JsonResponse

import json

from .models import Client, BankAccount, Transaction, SpendingCategory, Secret, Token

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

def generate_secret_model(request):
    # data.password, data.account_id
    if request.method == "POST":
        # TODO: verify user password
        # TODO: generate random secret (with unique id)
        # TODO: store secret in database
        # TODO: send back secret with id
        pass
    pass


def generate_secret(request):

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    # ------- Verify user password
    # Extract data from the request
    user_id = request.POST.get("user_id")
    given_password = request.POST.get("password") # TODO jsp si cest commme ca quil faut faire pour avoir la pwd ptdr
    account_number = request.POST.get("account_number")

    if not user_id or not given_password or not account_number:
        return JsonResponse({"status": "error", "message": "User ID, password, and account number are required"}, status=400)

    # Get the client instance
    user = get_object_or_404(Client, id=user_id)

    # Validate the password using check_password
    if not user.check_password(given_password):
        return JsonResponse({"status": "error", "message": "Invalid password"}, status=401)

    # Fetch the bank account associated with the user
    try:
        bank_account = BankAccount.objects.get(user=user, account_number=account_number)
    except BankAccount.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Bank account not found"}, status=404)

    # -------- Generate a secure secret
    secret_code = ''.join(random.choices(string.ascii_letters + string.digits, k=128))

    # -------- Create a new Secret object and store it in the database
    secret = Secret.objects.create(account=bank_account, code=secret_code, created_at=now())

    # -------- Return the secret and its ID
    # TODO dk if can send it back to app in this format
    return JsonResponse({
        "status": "success",
        "message": "Secret generated and stored successfully",
        "secret": secret_code,
        "id": secret.id
    })

def generate_token_model(request):
    # data.account_id, data.secret_id
    if request.method == "POST":
        # if no token id:
            # TODO: create token with challenge
            # TODO: store token in database
            # TODO: send back challenge with token id
        # else
            # TODO: check token challenge with secret
            # TODO: return token value
        pass
    pass


def generate_token(request):

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    # Extract data from the request
    account_id = request.POST.get("account_id")
    secret_id = request.POST.get("secret_id")
    token_id = request.POST.get("token_id", None)
    challenge = request.POST.get("challenge", None)

    if not account_id or not secret_id:
        return JsonResponse({"status": "error", "message": "Account ID and Secret ID are required"}, status=400)

    # Retrieve the Secret object
    secret = get_object_or_404(Secret, id=secret_id, account__id=account_id)

    # If no token_id is provided, create a new token with a challenge
    if not token_id:
        # TODO, dk if challenge/token should be random
        # Generate a random challenge
        challenge = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        # Generate a random token value
        token_value = ''.join(random.choices(string.ascii_letters + string.digits, k=64))

        # Create the token in the database
        token = Token.objects.create(
            account=secret.account,
            secret=secret,
            code=token_value,
            created_at=now(),
            expires_at=now() + timedelta(minutes=15)  # Tokens expire in 15 minutes
        )

        # Return the challenge and token ID
        # TODO dk if can send it back to app in this format
        return JsonResponse({
            "status": "success",
            "message": "Token created successfully",
            "token_id": token.id,
            "challenge": challenge
        })

    # If token_id is provided, validate the challenge
    else:
        # Retrieve the token object
        try:
            token = Token.objects.get(id=token_id, secret=secret)
        except Token.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Invalid token ID or secret"}, status=404)

        # Check if the token has expired
        if token.expires_at < now():
            return JsonResponse({"status": "error", "message": "Token has expired"}, status=403)

        # TODO validate the challenge

        # Return the token value
        return JsonResponse({
            "status": "success",
            "message": "Token validated successfully",
            "token_value": token.code
        })