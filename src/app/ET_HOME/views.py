from datetime import datetime

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from bank.models import BankAccount
from .models import Transaction, SpendingCategory


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirige vers une page d'accueil
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    return render(request, 'login.html')


def home_view(request):
    """
    Vue de la page d'accueil. Affiche une page d'accueil avec un message de bienvenue.
    """
    context = {}
    return render(request, 'dashboard.html', context)

def register_view(request):
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


def addBank_view(request):
    return render(request, 'add_bank.html')


def account_view(request):
    return render(request, 'account.html')


def settings_view(request):
    return render(request, 'settings.html')


def logout_view(request):
    return render(request, 'logout.html')


def get_bankAccount_info(request, id):
    try:
        account = BankAccount.objects.get(id=id)
        transactions = Transaction.objects.filter(account_id=id)

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

        account_data = [
            {
                "id" : str(account.id),
                "account_number" : account.account_number,
                "balance" : account.balance,
                "bank_name" : account.bank_name,
            }
        ]
        return JsonResponse({"account_data" : account_data, "transactions": transactions_data})

    except ValueError:
        return JsonResponse({"error": "Wrong account number."}, status=404)


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
