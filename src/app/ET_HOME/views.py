import base64
from datetime import datetime, timedelta
from io import BytesIO

import qrcode.main
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
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
    return render(request, "register.html")

def totp_setup_view(request):
    user: User = request.user
    if user.otp_activated:
        return redirect("settings")

    user.generate_otp_secret()
    qr = qrcode.main.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        border=4
    )
    qr.add_data(user.get_otp_uri())
    qr.make(fit=True)
    qr_img = qr.make_image()
    buffered = BytesIO()
    qr_img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    img_str = bytes("data:image/jpeg;base64,", encoding="utf-8") + img_str

    context = {
        "key": user.otp_secret,
        "qrcode": img_str.decode("utf-8")
    }
    return render(request, "totp_setup.html", context)


@login_required
def categories_view(request):
    start_date = datetime.today()
    start_date -= timedelta(days=start_date.day - 1)
    month = start_date.month
    year = start_date.year
    month += 1
    if month > 12:
        month -= 12
        year += 1
    end_date = datetime(year, month, 1)
    context = {
        "categories": SpendingCategory.objects.filter(user=request.user).annotate(
            total=Sum(
                "transaction__amount",
                filter=Q(
                    transaction__date__gte=start_date,
                    transaction__date__lt=end_date
                ),
                default=0
            )
        ).order_by("created_at")
    }
    return render(request, "categories.html", context)


@login_required
def add_account_view(request):
    return render(request, "add_account.html")


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
        "transactions": Transaction.objects.filter(user=request.user).order_by(sort_param)
    }

    return render(request, "transactions.html", context)


@login_required
def add_transaction_view(request):
    context = {
        "categories": SpendingCategory.objects.filter(user=request.user),
    }
    return render(request, "add_transaction.html", context)


@login_required
def transaction_view(request, id):
    transaction = get_object_or_404(Transaction, id=id, user=request.user)
    context = {
        "transaction": transaction,
        "categories": SpendingCategory.objects.filter(user=request.user)
    }
    return render(request, "transaction.html", context)
