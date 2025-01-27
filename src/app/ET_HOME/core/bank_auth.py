import hmac
from datetime import timedelta, datetime
from typing import Optional

import requests
from django.middleware.csrf import get_token
from django.urls import reverse
from django.utils.timezone import now

from ET_HOME.models import BankAccount, AppToken, Transaction, SpendingCategory


def generate_secret(request, user_id, account_number, password):
    csrf_token = get_token(request)
    response = requests.post(
        request.build_absolute_uri(reverse("bank:gen_secret")),
        {
            "user_id": user_id,
            "account_number": account_number,
            "password": password
        },
        headers={
            "X-CSRFToken": csrf_token
        },
        cookies={
            "csrftoken": csrf_token
        }
    )

    if response.status_code == 200:
        return response.json()
    return None

def generate_token(request, account_number, secret, secret_id):
    csrf_token = get_token(request)
    url = request.build_absolute_uri(reverse("bank:gen_token"))
    kwargs = {
        "headers": {
            "X-CSRFToken": csrf_token
        },
        "cookies": {
            "csrftoken": csrf_token
        }
    }

    # Request challenge
    response = requests.post(
        url,
        {
            "account_number": account_number,
            "secret_id": secret_id
        },
        **kwargs
    )

    res = response.json()
    if response.status_code != 200 or res.get("status") == "error":
        return None, res.get("message", "An error occurred while getting the challenge")

    challenge = res["challenge"]
    token_id = res["token_id"]

    # Reply with appropriate response
    swapped_challenge = challenge[16:] + challenge[:16]
    challenge_res = hmac.digest(bytes.fromhex(secret), bytes.fromhex(swapped_challenge), "SHA256").hex()

    response = requests.post(
        url,
        {
            "account_number": account_number,
            "secret_id": secret_id,
            "token_id": token_id,
            "challenge": challenge_res
        },
        **kwargs
    )

    res = response.json()
    if response.status_code != 200 or res.get("status") == "error":
        return None, res.get("message", "An error occurred while validating the challenge")

    token_data = res["token"]
    return token_data, None

def make_new_token(request, account):
    data, err = generate_token(request, account.account_number, account.secret, account.secret_id)
    if err is not None:
        print(f"ERROR: {err}")
        return None

    token = AppToken.objects.create(
        bank_token_id=data["id"],
        account=account,
        code=data["code"],
        created_at=now(),
        expires_at=data["expires_at"],
        activated=True
    )

    return token

def get_or_create_token(request, account: BankAccount):
    try:
        token = AppToken.objects.get(
            account=account,
            activated=True,
            expires_at__gt=now() + timedelta(seconds=10)
        )
    except AppToken.DoesNotExist:
        print("No valid token, recreating one")
        token = make_new_token(request, account)

    return token

def get_req(request, account, url):
    token = get_or_create_token(request, account)
    if token is None:
        print("Could not get valid token")
        return None

    csrf_token = get_token(request)
    url = request.build_absolute_uri(url)
    return requests.get(
        url,
        headers={
            "X-CSRFToken": csrf_token,
            "Authorization": "Bearer " + token.code
        },
        cookies={
            "csrftoken": csrf_token
        }
    )


def post_req(request, account, url, data):
    token = get_or_create_token(request, account)
    if token is None:
        print("Could not get valid token")
        return None

    csrf_token = get_token(request)
    url = request.build_absolute_uri(url)
    return requests.post(
        url,
        data,
        headers={
            "X-CSRFToken": csrf_token,
            "Authorization": "Bearer " + token.code
        },
        cookies={
            "csrftoken": csrf_token
        }
    )

def sync_account(request, account, from_date: Optional[datetime] = None):
    res = get_req(request, account, reverse("bank:get_account"))
    if res is not None and res.status_code == 200:
        data = res.json()
        if data["status"] != "success":
            return False

        data = data["data"]
        account.balance = data["balance"]
        account.account_number = data["account_number"]
        account.bank_name = data["bank_name"]
        account.save()

        return sync_transactions(request, account, from_date)
    else:
        return False

def sync_transactions(request, account: BankAccount, from_date: Optional[datetime] = None):
    if from_date is None:
        res = get_req(request, account, reverse("bank:get_transactions"))
    else:
        res = get_req(request, account, reverse("bank:get_transactions_from", kwargs={"from_date": from_date}))

    if res is not None and res.status_code == 200:
        data = res.json()
        if data["status"] != "success":
            return False

        data = data["data"]
        transactions = []
        for t in data:
            try:
                category = SpendingCategory.objects.get(
                    user=account.user,
                    name__iexact=t["category"]
                )
            except SpendingCategory.DoesNotExist:
                category = None

            transaction = Transaction(
                account=account,
                bank_transaction_id=t["id"],
                amount=t["amount"],
                category=category,
                date=t["date"],
                description=t["description"]
            )

            transactions.append(transaction)

        Transaction.objects.bulk_create(
            transactions,
            ignore_conflicts=True
        )
        return True
    return False