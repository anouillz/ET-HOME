import hmac
import json
import secrets
from datetime import timedelta

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
from django.views.decorators.http import require_GET, require_POST

from .api_utils import to_json
from .models import Client, BankAccount, Transaction, SpendingCategory, Secret, Token


@require_GET
def get_transaction(request, transactionId):
    transaction = Transaction.objects.filter(account=request.account, id=transactionId).first()
    if transaction:
        return JsonResponse({
            "status": "success",
            "data": to_json(transaction, Transaction),
            "message": "transaction found"
        }, status=200)
    else:
        return JsonResponse({
            "status": "error",
            "data": None,
            "message": "transaction not found"
        }, status=404)


@require_POST
def filter_transaction(request):
    try:
        data = json.loads(request.body)
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        categories = data.get('categories', [])

        if start_date:
            start_date = parse_datetime(start_date)
            if not start_date:
                return JsonResponse({"status": "error", "message": "Invalid start_date format. Use ISO 8601."}, status=400)
        if end_date:
            end_date = parse_datetime(end_date)
            if not end_date:
                return JsonResponse({"status": "error", "message": "Invalid end_date format. Use ISO 8601."}, status=400)

        if categories and not isinstance(categories, list):
            return JsonResponse({"status": "error", "message": "Categories should be an array."}, status=400)


        transactions = Transaction.objects.filter(account=request.account)

        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)

        if categories:
            db_categories = SpendingCategory.objects.filter(id__in=categories)
            transactions = transactions.filter(category__in=db_categories)

        return JsonResponse({
            "status": "success",
            "message": f"got transactions query",
            "data": to_json(transactions, Transaction, many=True)
        })

    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON body."}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@require_GET
def get_account(request, id):
    account = BankAccount.objects.filter(id=request.account.id)
    request.account = account
    return JsonResponse({
        "message": f"client {id} accounts",
        "status": "success",
        "data": to_json(request, many=False)
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
    account_number = request.POST.get("account_number")
    secret_id = request.POST.get("secret_id")
    token_id = request.POST.get("token_id", None)
    challenge = request.POST.get("challenge", None)

    if not account_number or not secret_id:
        return JsonResponse({"status": "error", "message": "Account ID and Secret ID are required"}, status=400)

    # Retrieve the Secret object
    secret = get_object_or_404(Secret, id=secret_id, account__account_number=account_number)

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
            challenge=challenge,
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

        swapped_challenge = token.challenge[16:] + token.challenge[:16]
        expected = hmac.digest(bytes.fromhex(secret.code), bytes.fromhex(swapped_challenge), "SHA256")

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

@require_POST
def add_transaction(request):
    try:

        account_id = request.POST.get("account_id")
        category_id = request.POST.get("category_id")
        amount = request.POST.get("amount")
        description = request.POST.get("description", "")

        if not all([account_id, category_id, amount]):
            return JsonResponse({"status": "error", "message": "All fields are required."}, status=400)

        account = get_object_or_404(BankAccount, id=account_id)
        category = get_object_or_404(SpendingCategory, id=category_id)

        # Create transaction
        transaction = Transaction.objects.create(
            account=account,
            amount=amount,
            description=description,
            category=category,
        )
        return JsonResponse({
            "status": "success",
            "message": "Transaction added successfully.",
            "id": transaction.id
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@require_POST
def add_account(request):
    try:

        account_number = request.POST.get("account_number")
        balance = request.POST.get("balance")
        bank_name = request.POST.get("bank_name")

        if not all([account_number, balance, bank_name]):
            return JsonResponse({"status": "error", "message": "All fields are required."}, status=400)

        user = get_object_or_404(Client, id=request.POST.get("user_id"))

        # Create bank account
        bank_account = BankAccount.objects.create(
            user=user,
            account_number=account_number,
            balance=balance,
            bank_name=bank_name,
        )
        return JsonResponse({
            "status": "success",
            "message": "Bank account added successfully.",
            "id": bank_account.id
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@require_POST
def add_category(request):
    try:
        name = request.POST.get("name")

        if not name:
            return JsonResponse({"status": "error", "message": "All fields are required."}, status=400)

        category = SpendingCategory.objects.create(name=name)
        return JsonResponse({
            "status": "success",
            "message": "Category added successfully.",
            "id": category.id
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

def add_account_view(request):
    context = {
        "clients": Client.objects.all(),
        "banks": ["UBS", "BCV", "BCVs", "Raiffeisen"]
    }
    return render(request, "bank/add_account.html", context)

def add_transaction_view(request):
    context = {
        "accounts": BankAccount.objects.all(),
        "categories": SpendingCategory.objects.all()
    }
    return render(request, "bank/add_transaction.html", context)

def add_category_view(request):
    return render(request, "bank/add_category.html")