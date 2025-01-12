from django.http import JsonResponse

import json

from django.http import JsonResponse

from .json_utils import open_json_file, get_json_client_from_id, get_json_client_from_name

JSON_URL = "src/app/bank/data.json"
def get_client_from_id(request,id):
    if request.method == 'GET':
        json_data = open_json_file(JSON_URL)
        client = get_json_client_from_id(json_data,id)
        return JsonResponse({'client': client})
    return JsonResponse({'client': ""})

def search_client(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            firstname = data.get('firstname')
            lastname = data.get('lastname') 
            json_data = open_json_file(JSON_URL)

            if not firstname or not lastname:
                return JsonResponse({'error': 'Both firstname and lastname are required'})
            client = get_json_client_from_name(json_data,firstname,lastname)

            return JsonResponse({"client":client})
        except json.JSONDecodeError:
            return JsonResponse({""})
    return JsonResponse({""})

def generate_secret(request):
    # data.password, data.account_id
    if request.method == "POST":
        # TODO: verify user password
        # TODO: generate random secret (with unique id)
        # TODO: store secret in database
        # TODO: send back secret with id
        pass
    pass

def generate_token(request):
    # data.account_id, data.secret_id
    if request.method == "POST":
        # if no token id:
            # TODO: create token with challenge
            # TODO: store token in database
            # TODO: send back challenge with token id
        # else
            # TODO: check token challenge with secret
            # TODO: return token value
        pass
    pass

# Create your views here.
