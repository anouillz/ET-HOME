from django.shortcuts import render
from django.http import JsonResponse
from .json_utils import open_json_file,get_json_client_from_id,get_json_client_from_name
import json
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





# Create your views here.
