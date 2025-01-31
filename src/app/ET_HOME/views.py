import time
from datetime import datetime, timedelta
from typing import Optional

from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from .core import bank_auth
from .models import Transaction, SpendingCategory, User, BankAccount, Notification, NotificationType
from .serializers import NotificationSerializer, TransactionSerializer, FullSpendingCategorySerializer, \
    TransactionWithoutCategorySerializer, FullBankAccountSerializer, \
    TransactionWithoutAccountSerializer, UserSerializer, BareTransactionSerializer


def api_access(request):
    return render(request, 'api.html')


def get_transactions(request, first_date: datetime.date, second_date: datetime.date):
    transactions = Transaction.objects.filter(
        account__user=request.user,
        date__gte=first_date,
        date__lt=second_date + timedelta(days=1)
    ).order_by("date")
    return JsonResponse({
        "status": "success",
        "transactions": TransactionSerializer(transactions, many=True).data
    })


def get_account_transactions(request, id, first_date, second_date):
    transactions = Transaction.objects.filter(
        account_id=id,
        date__gte=first_date,
        date__lt=second_date + timedelta(days=1)
    ).order_by("date")
    return JsonResponse({
        "status": "success",
        "transactions": TransactionSerializer(transactions, many=True).data
    })


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


@login_required
def categories(request):
    if request.method == "GET":
        categories = SpendingCategory.objects.filter(user=request.user)
        return JsonResponse({
            "status": "success",
            "categories": FullSpendingCategorySerializer(categories, many=True).data
        })
    elif request.method == "POST":
        name = request.POST.get("name")
        budget = request.POST.get("user_budget")

        try:
            category = SpendingCategory.objects.create(
                name=name,
                user_budget=budget,
                user=request.user
            )
        except IntegrityError:
            return JsonResponse({
                "status": "error",
                "error": "Already exists"
            })

        return JsonResponse({
            "status": "success",
            "category": FullSpendingCategorySerializer(category).data
        })


@login_required
def category(request, id):
    category = get_object_or_404(SpendingCategory, id=id, user=request.user)
    if request.method == "GET":
        transactions = Transaction.objects.filter(category=category)
        return JsonResponse({
            "status": "success",
            "category": FullSpendingCategorySerializer(category).data,
            "transactions": TransactionWithoutCategorySerializer(transactions, many=True).data
        })
    elif request.method == "POST":
        if not category.is_default:
            category.name = request.POST.get("name", category.name)
        category.user_budget = request.POST.get("user_budget", category.user_budget)
        category.save()
        return JsonResponse({
            "status": "success",
            "category": FullSpendingCategorySerializer(category).data
        })
    elif request.method == "DELETE":
        category.delete()
        return JsonResponse({
            "status": "success"
        })
    else:
        return JsonResponse({
            "status": "error",
            "error": "Unsupported method"
        }, status=HTTP_400_BAD_REQUEST)


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
    return render(request, "settings.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def get_account(request, id):
    account = get_object_or_404(BankAccount, id=id, user=request.user)

    # Only get transactions from the beginning of last month
    today = datetime.today()
    start_date = datetime(today.year, today.month, 1)
    start_date += relativedelta(months=-1)
    start_date = start_date.date()
    transactions = Transaction.objects.filter(
        account=account,
        date__gte=start_date
    )

    return JsonResponse({
        "status": "success",
        "account": FullBankAccountSerializer(account).data,
        "transactions": TransactionWithoutAccountSerializer(transactions, many=True).data
    })


@login_required
def get_accounts(request):
    accounts = BankAccount.objects.filter(user=request.user)
    return JsonResponse({
        "status": "success",
        "accounts": FullBankAccountSerializer(accounts, many=True).data
    })


@login_required
def get_outcomes(request, first_date, second_date):
    transactions = Transaction.objects.filter(
        user=request.user,
        date__gte=first_date,
        date__lte=second_date,
        amount__lt=0
    )
    total = transactions.aggregate(total=Sum("amount"))["total"]

    return JsonResponse({
        "status": "success",
        "dates": {
            "start_date": first_date,
            "end_date": second_date
        },
        "total_outcome": -total,
        "transactions": TransactionSerializer(transactions, many=True).data
    })


@login_required
def get_incomes(request, first_date, second_date):
    transactions = Transaction.objects.filter(
        user=request.user,
        date__gte=first_date,
        date__lte=second_date,
        amount__gt=0
    )
    total = transactions.aggregate(total=Sum("amount"))["total"]

    return JsonResponse({
        "status": "success",
        "dates": {
            "start_date": first_date,
            "end_date": second_date
        },
        "total_income": total,
        "transactions": TransactionSerializer(transactions, many=True).data
    })


def check_category(request, category: SpendingCategory):
    transactions = Transaction.objects.filter(
        account__user=request.user,
        category=category,
        amount__lt=0
    )
    total = transactions.aggregate(total=Sum("amount"))["total"]
    budget = category.user_budget
    if category:
        message = None
        if total > budget:
            delta = total - budget
            message = f"You have exceeded your budget by CHF {delta} for the category {category.name}"

        elif total == budget:
            message = f"You have used all your budget for the category {category.name}, please be careful"

        elif (budget - total) / budget < 0.1:
            delta = budget - total
            message = f"Be careful ! You have CHF {delta} left in your budget for the category {category.name}"

        if message is not None:
            Notification.objects.create(
                user=request.user,
                type=NotificationType.BUDGET,
                related_object_id=category.id,
                message=message
            )


@require_POST
def add_transaction(request):
    category_id = request.POST.get("category_id")
    category = get_object_or_404(SpendingCategory, user=request.user, id=category_id)
    amount = request.POST.get("amount")
    date = request.POST.get("date")
    description = request.POST.get("description")
    if not amount or not date or not description:
        return JsonResponse({
            "status": "error",
            "error": "Amount, date and description are required"
        }, status=HTTP_400_BAD_REQUEST)

    transaction = Transaction.objects.create(
        user=request.user,
        amount=amount,
        date=date,
        description=description,
        category=category
    )
    transaction.save()
    check_category(request, category)
    return JsonResponse({
        "status": "success",
        "transaction": TransactionSerializer(transaction).data
    })


@require_POST
@login_required
def add_bank_account(request):
    res = bank_auth.generate_secret(
        request,
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

        bank_auth.sync_account(request, account)

        message = f"Successfully added new bank account into your app ({account.account_number})"
        Notification.objects.create(
            user=request.user,
            related_object_id=account.id,
            type=NotificationType.ACCOUNT,
            message=message
        )
        return JsonResponse({
            "status": "success",
            "account": FullBankAccountSerializer(account).data
        }, status=HTTP_201_CREATED)

    return JsonResponse({
        "status": "error",
        "error": "An error occurred, could not generate secret"
    }, status=HTTP_400_BAD_REQUEST)


@require_POST
@login_required
def test_secret(request):
    account_id = request.POST.get("account_id")
    account = get_object_or_404(BankAccount, id=account_id)
    data, error = bank_auth.generate_token(
        request,
        account.account_number,
        account.secret,
        account.secret_id
    )

    # Artificial delay
    time.sleep(3)
    if data is not None:
        return JsonResponse({
            "status": "success"
        })
    return JsonResponse({
        "status": "error",
        "error": error
    }, status=HTTP_400_BAD_REQUEST)


@require_POST
@login_required
def add_category(request):
    category_name = request.POST.get("name")
    user_budget = request.POST.get("user_budget")

    if not category_name or not user_budget:
        return JsonResponse({
            "status": "error",
            "error": "Category name and budget are required"
        }, status=HTTP_400_BAD_REQUEST)


    # check if the category already exists
    if SpendingCategory.objects.filter(name=category_name, user=request.user).exists():
        return JsonResponse({
            "status": "error",
            "error": "Category already exists"
        }, status=HTTP_400_BAD_REQUEST)

    category = SpendingCategory.objects.create(
        name=category_name,
        user=request.user,
        user_budget=user_budget
    )

    return JsonResponse({
        "status": "success",
        "category": FullSpendingCategorySerializer(category).data
    })


@require_POST
@login_required
def delete_category(request):
    category_id = request.POST.get("category_id")

    if not category_id:
        return JsonResponse({
            "status": "error",
            "error": "Category ID is required"
        }, status=HTTP_400_BAD_REQUEST)

    category = get_object_or_404(SpendingCategory, id=category_id, user=request.user)
    if category.is_default:
        return JsonResponse({
            "status": "error",
            "error": "Cannot delete default category"
        })

    category.delete()
    return JsonResponse({"status": "success"})

@login_required
def transactions_view(request):
    context = {
        "transactions": Transaction.objects.filter(account__user=request.user)
    }
    return render(request, "transactions.html", context)






def update_category_budget(request):
    category_id = request.POST.get("category_id")
    new_budget = float(request.POST.get("new_budget"))
    if not category_id or not new_budget:
        return JsonResponse({
            "status": "error",
            "error": "category_id and new_budget are required"
        }, status=HTTP_400_BAD_REQUEST)

    category = get_object_or_404(SpendingCategory, id=category_id, user=request.user)
    category.user_budget = new_budget
    category.save()
    return JsonResponse({
        "status": "success",
        "category": FullSpendingCategorySerializer(category).data
    })


# TODO
# change password
def change_password(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")

        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not current_password or not new_password or not confirm_password:
            messages.error(request, "All fields are required.")
            return redirect("change_password.html")

        # Authenticate the current password
        # check if the current password is correct
        user = authenticate(username=request.user.username, password=current_password)
        if user is None:
            messages.error(request, "Current password is incorrect.")
            return redirect("change_password.html")

        # Check if the new password and confirmation match
        if new_password != confirm_password:
            messages.error(request, "New password and confirmation do not match.")
            return redirect("change_password.html")

        # Update the password
        user.set_password(new_password)
        user.save()

        # Re-authenticate and log the user in after password change
        login(request, user)
        messages.success(request, "Password updated successfully.")
        return redirect('account.html')  # Replace "profile" with the desired redirect URL

    # create a form to change the password
    return render(request, "change_password.html")


@require_POST
@login_required
def export_data(request):
    password = request.POST.get("password")

    if not request.user.check_password(password):
        return JsonResponse({
            "status": "error",
            "error": "Invalid password"
        }, status=HTTP_401_UNAUTHORIZED)

    bank_accounts = BankAccount.objects.filter(user=request.user)
    categories = SpendingCategory.objects.filter(user=request.user)
    transactions = Transaction.objects.filter(user=request.user)

    export_file = {
        "user": UserSerializer(request.user).data,
        "accounts": FullBankAccountSerializer(bank_accounts, many=True).data,
        "categories": FullSpendingCategorySerializer(categories, many=True).data,
        "transactions": BareTransactionSerializer(transactions, many=True).data
    }

    return JsonResponse(export_file)


@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    return JsonResponse({
        "status": "success",
        "notifications": NotificationSerializer(notifications, many=True).data
    })

@require_POST
@login_required
def read_notification(request, id):
    notification = get_object_or_404(Notification, user=request.user, id=id)
    notification.is_read = True
    notification.save()
    return JsonResponse({"status": "success"})


@require_POST
@login_required
@csrf_exempt
def sync_user(request, from_date: Optional[datetime] = None):
    user = None
    if request.user.is_authenticated:
        user = request.user
    user_id = request.POST.get("user_id")
    if user_id is not None:
        user = get_object_or_404(User, id=user_id)

    if user is None:
        return JsonResponse({"status": "error", "error": "No user set"}, status=HTTP_400_BAD_REQUEST)

    accounts = BankAccount.objects.filter(user=user)

    data = {}
    for account in accounts:
        print(f"Syncing account {account.id}")
        synced = bank_auth.sync_account(request, account, from_date)
        data[str(account.id)] = synced

    return JsonResponse({"status": "success", "data": data})


@require_POST
@csrf_exempt
def sync_account(request, account_number, from_date: Optional[datetime] = None):
    account = get_object_or_404(BankAccount, account_number=account_number)
    print(f"Syncing account {account.id}")
    synced = bank_auth.sync_account(request, account, from_date)

    return JsonResponse({"status": "success", "synced": synced})