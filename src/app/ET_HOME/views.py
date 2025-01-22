import time
from datetime import datetime
import json
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK
from .serializers import NotificationSerializer
from .core import bank_auth
from .models import Transaction, SpendingCategory, User, BankAccount,Notification


def api_access(request):
    return render(request, 'api.html')

def get_transactions(request, first_date, second_date):
    transactions = Transaction.objects.filter(
        account__user=request.user,
        date__gte=first_date,
        date__lte=second_date
    ).order_by("date")
    transactions_data = []
    for transaction in transactions:
        transactions_data.append({
            "id": str(transaction.id),
            "account": transaction.account.id,
            "amount": float(transaction.amount),
            "date": transaction.date.isoformat(),
            "description": transaction.description,
            "category": transaction.category.id if transaction.category else None,
        })
    return JsonResponse({"transactions": transactions_data})

def get_account_transactions(request, id, first_date, second_date):
    transactions = Transaction.objects.filter(
        account_id=id,
        date__gte=first_date,
        date__lte=second_date
    ).order_by("date")
    transactions_data = []
    for transaction in transactions:
        transactions_data.append({
            "id": str(transaction.id),
            "account": transaction.account.id,
            "amount": float(transaction.amount),
            "date": transaction.date.isoformat(),
            "description": transaction.description,
            "category": transaction.category.id if transaction.category else None,
        })
    return JsonResponse({"transactions": transactions_data})

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

@login_required
def get_categories(request):
    categories = SpendingCategory.objects.filter(user=request.user)

    categories_data = [
        {
            "id": str(category.id),
            "name": category.name,
            "default": category.is_default
        }
        for category in categories
    ]
    return JsonResponse({"categories": categories_data}, status=HTTP_200_OK)

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


# main views
@login_required
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

        default_categories = [
            {"name": "Food", "default_budget": 1000.00},
            {"name": "Bills", "default_budget": 1500.00},
            {"name": "Entertainment", "default_budget": 200.00},
            {"name": "Health", "default_budget": 300.00},
            {"name": "Gifts", "default_budget": 100.00},
            {"name": "Transport", "default_budget": 200.00}
        ]

        for category in default_categories:
            SpendingCategory.objects.create(
                user=user,
                name=category["name"],
                default_budget=category["default_budget"],
                is_default=True
            )

        return redirect("login")

    return render(request, 'register.html')

def category_view(request):
    return render(request, 'categories.html')


@login_required
def add_account_view(request):
    return render(request, 'add_account.html')

@login_required
def account_view(request):
    return render(request, 'account.html')

@login_required
def dashboard_view(request):
    """
    Vue de la page d'accueil. Affiche une page d'accueil avec un message de bienvenue.
    """
    context = {
        "user": request.user
    }
    return render(request, 'dashboard.html', context)

@login_required
def settings_view(request):
    return render(request, 'settings.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
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

@login_required
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
@login_required
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
@login_required
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

# categories functions
@login_required
def add_category(request):
    if request.method == "POST":
        category_name = request.POST.get("name")
        user_budget = request.POST.get("user_budget")

        if not category_name or not user_budget:
            return JsonResponse({"new category status": "error", "message": "Category name and budget are required"}, status=400)

        try:
            # Check if a category with the same name already exists for this user
            if SpendingCategory.objects.filter(name=category_name, user=request.user).exists():
                return JsonResponse({"new category status": "error", "message": "Category with this name already exists"}, status=400)

            # Create the new category with the custom budget
            category = SpendingCategory.objects.create(
                name=category_name,
                user=request.user,
                user_budget=user_budget,
                is_default=False
            )
            category.save()
            return JsonResponse({"new category status": "success", "category_id": category.id})
        except Exception as e:
            return JsonResponse({"new category status": "error", "message": str(e)}, status=500)

    return JsonResponse({"new category status": "error", "message": "Invalid request method"}, status=400)


@login_required
def delete_category(request):
    if request.method == "POST":
        category_name = request.POST.get("name")
        if not category_name:
            return JsonResponse({"delete category status": "error", "message": "Category name is required"}, status=400)

        try:
            # ensure the category belongs to the user and is not a default category
            category = SpendingCategory.objects.get(name=category_name, user=request.user, is_default=False)
            category.delete()
            return JsonResponse({"delete category status": "success"})
        except SpendingCategory.DoesNotExist:
            return JsonResponse(
                {"delete category status": "error", "message": "Category not found or cannot be deleted"}, status=404)
    else:
        return JsonResponse({"delete category status": "error", "message": "Invalid request method"}, status=400)

@login_required
def modify_category(request):
    if request.method == "POST":
        category_name = request.POST.get("name")

        # depends on what the user wants to modify
        new_name = request.POST.get("new_name")
        new_budget = request.POST.get("new_budget")

        if not category_name or not new_name or not new_budget:
            return JsonResponse({
                "modify category status": "error",
                "message": "Name, new name, and new budget are required"
            }, status=400)

        try:
            # ensure the category belongs to the user and is not a default category
            category = SpendingCategory.objects.get(name=category_name, user=request.user, is_default=False)

            # check if the new name is already in use by another category
            if SpendingCategory.objects.filter(name=new_name, user=request.user).exclude(id=category.id).exists():
                return JsonResponse({
                    "modify category status": "error",
                    "message": "A category with the new name already exists"
                }, status=400)

            # Update the category
            category.name = new_name
            category.user_budget = new_budget
            category.save()

            return JsonResponse({"modify category status": "success"})
        except SpendingCategory.DoesNotExist:
            return JsonResponse({
                "modify category status": "error",
                "message": "Category not found or cannot be modified"
            }, status=404)
    else:
        return JsonResponse({
            "modify category status": "error",
            "message": "Invalid request method"
        }, status=400)

# change password
@login_required
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
    return render(request, "change_password")


def export_data(request):
    if request.method == 'POST':

        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON received."}, status=400)

        if not user_id:
            return JsonResponse({"error": "User ID is required."}, status=400)

        bank_accounts = BankAccount.objects.filter(user_id=user_id)

        if not bank_accounts.exists():
            return JsonResponse({"error": "No data found for the given user ID."}, status=404)

        export_file = {
            "user_id": user_id,
            "bank_accounts": []
        }

        for bank_account in bank_accounts:
            bank_account_data = {
                "id": str(bank_account.id),
                "account_number": bank_account.account_number,
                "balance": float(bank_account.balance),
                "bank_name": bank_account.bank_name,
                "transactions": []
            }
            transactions = Transaction.objects.filter(account=bank_account)

            for transaction in transactions:
                category = SpendingCategory.objects.filter(id=transaction.category_id).first()
                transaction_data = {
                    "id": str(transaction.id),
                    "amount": float(transaction.amount),
                    "date": transaction.date.isoformat(),
                    "description": transaction.description,
                    "category": category.name,
                }
                bank_account_data["transactions"].append(transaction_data)

            export_file["bank_accounts"].append(bank_account_data)

        return JsonResponse(export_file, safe=False, status=200)



def get_notifications(request):
    notifications = Notification.objects.filter(user=request.user,is_read=False)
    return JsonResponse({
        "message":"user not readed notifications",
        "status":"success",
        "notifications":NotificationSerializer(notifications,many=True).data
    })


def read_notification(request,id):
    notification = Notification.objects.filter(user=request.user,id=id).first()
    if notification:
        notification.is_read = True
        notification.save()
        return JsonResponse({
            "message":"notification"+id+" successfully read",
            "status":"success"
        })
    return JsonResponse({
        "message":"notification does not exist",
        "status":"error"
    })