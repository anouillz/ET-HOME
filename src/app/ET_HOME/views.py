from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .models import Transaction, SpendingCategory, User, BankAccount


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "login.html")


def create_default_categories(user):
    default_categories = [
        {"name": "Food", "budget": 200.00},
        {"name": "Transport", "budget": 100.00},
        {"name": "Entertainment", "budget": 150.00},
        {"name": "Health", "budget": 80.00},
        {"name": "Gifts", "budget": 50.00},
        {"name": "Bills", "budget": 100.00},
    ]

    for category in default_categories:
        SpendingCategory.objects.create(
            name=category["name"],
            user=user,
            is_default=True,  # category cannot be deleted
            user_budget=category["budget"]
        )


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

        create_default_categories(user)

        return redirect("login")

    return render(request, 'register.html')


@login_required
def categories_view(request):
    context = {
        "categories": SpendingCategory.objects.filter(user=request.user)
    }
    return render(request, "categories.html", context)


@login_required
def add_account_view(request):
    return render(request, "add_account.html")


@login_required
def account_view(request):
    return render(request, "account.html")


@login_required
def dashboard_view(request):
    context = {
        "user": request.user
    }
    return render(request, "dashboard.html", context)


@login_required
def settings_view(request):
    context = {
        "accounts": BankAccount.objects.filter(user=request.user).order_by("added_at"),
        "user": request.user
    }
    return render(request, "settings.html", context)


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def transactions_view(request):
    sort_param = request.GET.get("sort", "date")
    if sort_param not in ["date", "category", "amount"]:
        sort_param = "date"
    context = {
        "transactions": Transaction.objects.filter(
            Q(account__user=request.user) | Q(account=None)
        ).order_by(sort_param)
    }

    return render(request, "transactions.html", context)


@login_required
def add_expenses_view(request):
    context = {
        "categories": SpendingCategory.objects.filter(user=request.user),
    }
    return render(request, 'add_expenses.html', context)


@login_required
def transaction_view(request, id):
    transaction = get_object_or_404(Transaction, id=id, user=request.user)
    context = {
        "transaction": transaction,
        "categories": SpendingCategory.objects.filter(user=request.user)
    }
    return render(request, "transaction.html", context)
