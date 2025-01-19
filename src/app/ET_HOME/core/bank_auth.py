import hmac

import requests
from django.middleware.csrf import get_token
from django.urls import reverse


def generate_secret(request, user_id, account_number, password):
    csrf_token = get_token(request)
    response = requests.post(
        request.build_absolute_uri(reverse("gen_secret")),
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
    url = request.build_absolute_uri(reverse("gen_token"))
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

    token_value = res["token_value"]
    return token_value, None