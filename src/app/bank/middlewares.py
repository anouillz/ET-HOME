from functools import wraps

from django.http import HttpResponse
from django.utils.timezone import now
from rest_framework.status import HTTP_401_UNAUTHORIZED

from bank.models import Token


def check_token_validity(request):
    token_code = request.META.get("HTTP_AUTHORIZATION")
    if not isinstance(token_code, str) or not token_code.startswith("Bearer "):
        return False
    token_code = token_code.replace("Bearer ", "")
    try:
        token = Token.objects.get(code=token_code)
    except Token.DoesNotExist:
        print("Token does not exist")
        return False

    if not token.activated:
        print("Token is not activated")
        return False

    if token.expires_at < now():
        print("Token has expired")
        return False

    request.account = token.account
    return True

def token_protected(view_function):
    @wraps(view_function)
    def wrap(request, *args, **kwargs):
        if not check_token_validity(request):
            return HttpResponse("Unauthorized", status=HTTP_401_UNAUTHORIZED)
        return view_function(request, *args, **kwargs)
    return wrap