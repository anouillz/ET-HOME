import json
def open_json_file(url):
    file = open(url,'r')
    json_data = json.loads(file.read())
    file.close()
    return json_data

def get_json_client_from_id(json_data,id):
    try:
        for client in json_data['clients']:
            if "id" in client and client["id"] == str(id):
                return client
        return None
    except:
        return None

def get_json_client_from_name(json_data,firstname,lastname):
    if "clients" not in json_data:
        return ""
    for client in json_data:
        if "id" in client and client["firstname"] == firstname and client["lastname"] == lastname:
            return client
    return None
