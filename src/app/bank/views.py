import hmac
import json
import secrets
from datetime import timedelta

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models.utils import get_or_none
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from .models import Client, BankAccount, Transaction, SpendingCategory, Secret, Token

def get_client(request):
    if request.method == 'GET':
        id = request.user.id
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

def get_transaction(request,transactionId):
    userId = request.user.id
    if request.method == 'GET':
        transaction = get_or_none(Transaction,id=transactionId,user__id=userId)
        if transaction == None:
            return JsonResponse({
                'transaction':None,
                'message':"Transaction does not exist"
            })
        return JsonResponse({
                'transaction':transaction,
                'message':""
            })

    


def generate_secret(request):

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    # ------- Verify user password
    # Extract data from the request
    user_id = request.POST.get("user_id")
    given_password = request.POST.get("password")
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
    secret_code = secrets.token_hex(64)

    # -------- Create a new Secret object and store it in the database
    secret = Secret.objects.create(account=bank_account, code=secret_code, created_at=now())

    # -------- Return the secret and its ID
    return JsonResponse({
        "status": "success",
        "message": "Secret generated and stored successfully",
        "secret": secret_code,
        "id": secret.id
    })


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
    secret = get_object_or_404(Secret, id=secret_id, account_id=account_id)

    # If no token_id is provided, create a new token with a challenge
    if not token_id:
        # TODO, dk if challenge/token should be random
        # Generate a random challenge
        challenge = secrets.token_hex(16)

        # Generate a random token value
        token_value = secrets.token_hex(64)

        # Create the token in the database
        token = Token.objects.create(
            account=secret.account,
            secret=secret,
            code=token_value,
            created_at=now(),
            expires_at=now() + timedelta(minutes=60)  # Tokens expire in 60 minutes
        )

        # Return the challenge and token ID
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

        if token.activated:
            return JsonResponse({"status": "error", "message": "Token already activated"}, status=403)

        swapped_token = token.challenge[16:] + token.challenge[:16]
        expected = hmac.digest(bytes.fromhex(secret.code), bytes.fromhex(swapped_token), "SHA256")

        if not hmac.compare_digest(expected, bytes.fromhex(challenge)):
            return JsonResponse({
                "status": "error",
                "message": "Incorrect response"
            }, status=401)

        # Return the token value
        return JsonResponse({
            "status": "success",
            "message": "Token validated successfully",
            "token_value": token.code
        })


def validate_token(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    # get token
    token = request.POST.get("token")
    token_id = request.POST.get("token_id")

    if not token_id:
        return JsonResponse({"status": "error", "message": "Token is required"}, status=400)
    else:
        token = get_object_or_404(Token, id=token_id)

        if token.code == token:
            token.activated = True
            token.save()
            return JsonResponse({"status": "success", "message": "Token validated successfully"})
        else:
            return JsonResponse({"status": "error", "message": "Invalid token"}, status=401)

