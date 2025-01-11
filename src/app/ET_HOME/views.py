from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
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
    context = {
        'title': 'Bienvenue',
        'message': 'Bienvenue sur notre site Django !',
    }
    return render(request, 'home.html', context) 

def register_view(request):
    return render(request, 'register.html') 

def api_access(request):
    return render(request, 'api.html')

def get_transactions(request, date):

    if date == "all":
        return get_all_transactions(request)

    try:
        transactions = Transaction.objects.filter(date=date)
        transactions_data = [
          {
                "id": str(transaction.id),
               "account": transaction.account.id,
                "amount": float(transaction.amount),
                "date": transaction.date.isoformat(),
               "description": transaction.description,
                "category": transaction.category.id if transaction.category else None,
            }
            for transaction in transactions
        ]
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
    return JsonResponse({"transactions": transactions_data})

def get_spending_per_category(request, category):
    try:
        spending_category = SpendingCategory.objects.get(id=category)
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

