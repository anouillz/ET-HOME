import time
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK

from .core import bank_auth
from .models import Transaction, SpendingCategory, User, BankAccount


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirige vers une page d'accueil
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    return render(request, 'login.html')


def dashboard_view(request):
    """
    Vue de la page d'accueil. Affiche une page d'accueil avec un message de bienvenue.
    """
    context = {
        "user": request.user
    }
    return render(request, 'dashboard.html', context)

def register_view(request):
    if request.method == "POST":
        user = User.objects.create_user(
            username=request.POST["username"],
            email=request.POST["email"],
            password=request.POST["password"],
        )

        user.first_name = request.POST["firstname"]
        user.last_name = request.POST["lastname"]
        user.save()
        return redirect("login")
    return render(request, 'register.html')

def api_access(request):
    return render(request, 'api.html')

def get_transactions(request, first_date, second_date):
    try:
        transactions = Transaction.objects.all()
        first_date = datetime.strptime(first_date, "%Y-%m-%d").date()
        second_date = datetime.strptime(second_date, "%Y-%m-%d").date()
        transactions_data = []
        for transaction in transactions:
            transaction_date = transaction.date.date()
            if first_date <= transaction_date <= second_date:
                transactions_data.append(
                  {
                       "id": str(transaction.id),
                       "account": transaction.account.id,
                       "amount": float(transaction.amount),
                       "date": transaction.date.isoformat(),
                       "description": transaction.description,
                       "category": transaction.category.id if transaction.category else None,
                  }
                )
        return JsonResponse({"transactions": transactions_data})
    except ValueError:
        return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS."}, status=400)




def get_all_transactions(request):
    transactions = Transaction.objects.all()
    transactions_data = [
        {
            "id": str(transaction.id),
            "account": transaction.account.id,
            "amount": float(transaction.amount),
            "date": transaction.date.isoformat(),
            "description": transaction.description,
            "category": transaction.category.name if transaction.category else None,
        }
        for transaction in transactions
    ]
    return transactions_data



def get_category(request, id):
    try:
        spending_category = SpendingCategory.objects.get(id=id)
        transactions = Transaction.objects.filter(category=spending_category)

        transactions_data = [
            {
                "id": str(transaction.id),
                "account": transaction.account.id,
                "amount": float(transaction.amount),
                "date": transaction.date.isoformat(),
                "description": transaction.description,
                "category": transaction.category.name,
            }
            for transaction in transactions
        ]
        return JsonResponse({"category": spending_category.name, "transactions": transactions_data})

    except SpendingCategory.DoesNotExist:
        return JsonResponse({"error": "Spending category not found."}, status=404)


def category_view(request):
    return render(request, 'categories.html')


def add_account_view(request):
    return render(request, 'add_account.html')


def account_view(request):
    return render(request, 'account.html')


def settings_view(request):
    return render(request, 'settings.html')


def logout_view(request):
    return render(request, 'logout.html')


def get_bankAccount_info(request, id):
    try:
        account = BankAccount.objects.get(id=id)
        # Only get transactions from the beginning of last month
        today = datetime.today()
        start_date = datetime(today.year, today.month, 1)
        start_date += relativedelta(months=-1)
        start_date = start_date.date()
        transactions = Transaction.objects.filter(
            account_id=id,
            date__gte=start_date.isoformat()
        )

        transactions_data = [
            {
                "id": str(transaction.id),
                "account": transaction.account.id,
                "amount": float(transaction.amount),
                "date": transaction.date.isoformat(),
                "description": transaction.description,
                "category": {
                    "id": str(transaction.category.id),
                    "name": transaction.category.name
                }
            }
            for transaction in transactions
            if start_date <= transaction.date.date()
        ]

        account_data = {
            "id" : str(account.id),
            "account_number" : account.account_number,
            "balance" : float(account.balance),
            "bank_name" : account.bank_name,
        }

        return JsonResponse({"account_data" : account_data, "transactions": transactions_data})

    except ValueError as e:
        print(e)
        return JsonResponse({"error": "Wrong account number."}, status=404)

def get_accounts(request):
    try:
        accounts = BankAccount.objects.filter(user__id=request.user.id)
        accounts_data = [
            {
                "id": str(account.id),
                "bank": account.bank_name,
                "balance": float(account.balance),
                "account_number": account.account_number
            }
            for account in accounts
        ]

        return JsonResponse({"accounts": accounts_data})
    except ValueError:
        return JsonResponse({"error": "An error occured"}, status=500)

def get_outcomes(request, first_date, second_date):
    try:
        transactions = Transaction.objects.all()
        first_date = datetime.strptime(first_date, "%Y-%m-%d").date()
        second_date = datetime.strptime(second_date, "%Y-%m-%d").date()
        outcome = 0
        transactions_data = []
        for transaction in transactions:
            transaction_date = transaction.date.date()
            if first_date <= transaction_date <= second_date and transaction.amount < 0:
                outcome += transaction.amount
                transactions_data.append(
                    {
                        "id": str(transaction.id),
                        "account": transaction.account.id,
                        "amount": float(transaction.amount),
                        "date": transaction.date.isoformat(),
                        "description": transaction.description,
                        "category": transaction.category.id if transaction.category else None,
                    }
                )
        return JsonResponse({"dates": {"start_date": first_date, "end_date": second_date}, "outcome": outcome, "transactions": transactions_data})
    except ValueError:
        return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS."}, status=400)


def get_incomes(request, first_date, second_date):
    try:
        transactions = Transaction.objects.all()
        first_date = datetime.strptime(first_date, "%Y-%m-%d").date()
        second_date = datetime.strptime(second_date, "%Y-%m-%d").date()
        incomes = 0
        transactions_data = []
        for transaction in transactions:
            transaction_date = transaction.date.date()
            if first_date <= transaction_date <= second_date and transaction.amount >= 0:
                incomes += transaction.amount
                transactions_data.append(
                    {
                        "id": str(transaction.id),
                        "account": transaction.account.id,
                        "amount": float(transaction.amount),
                        "date": transaction.date.isoformat(),
                        "description": transaction.description,
                        "category": transaction.category.id if transaction.category else None,
                    }
                )
        return JsonResponse({"dates": {"start_date": first_date, "end_date": second_date}, "income": incomes, "transactions": transactions_data})
    except ValueError:
        return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS."}, status=400)

def add_transactions(request):
    if request.method == "POST":
        transaction = Transaction.objects.create(
            id = request.POST['id'],
            account_id = request.POST['account id'],
            amount = request.POST['amount'],
            date = request.POST['date'],
            description = request.POST['description'],
            category_id = request.POST['category id'],
        )
        transaction.save()
        return JsonResponse({"new transaction status": "success"})
    else:
        return JsonResponse({"new transaction status": "error"}, status=400)
@require_POST
def add_bank_account(request):
    res = bank_auth.generate_secret(
        request,
        request.POST.get("user_id"),
        request.POST.get("account_number"),
        request.POST.get("password")
    )

    # Artificial delay
    time.sleep(3)
    if res is not None:
        account = BankAccount.objects.create(
            account_number=request.POST.get("account_number"),
            balance=0,
            bank_name=request.POST.get("bank_name"),
            user=request.user,
            secret=res.get("secret"),
            secret_id=res.get("id")
        )
        return JsonResponse({
            "id": account.id
        }, status=HTTP_201_CREATED)
    return JsonResponse({"error": "An error occurred"}, status=HTTP_400_BAD_REQUEST)

@require_POST
def test_secret(request):
    account = get_object_or_404(BankAccount, id=request.POST.get("account_id"))
    token, error = bank_auth.generate_token(
        request,
        account.account_number,
        account.secret,
        account.secret_id
    )

    # Artificial delay
    time.sleep(3)
    if token is not None:
        return JsonResponse({"status": "Connection successful"}, status=HTTP_200_OK)
    return JsonResponse({"error": error}, status=HTTP_400_BAD_REQUEST)