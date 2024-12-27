#MOCKUP OF THE APPLICATION

#API FUNCTIONS
def connect_to_bank_API(key):
    print("Should connect to the bank API")
def disconnect_from_bank_API():
    print("Should disconnect from the bank API")

#CONNECT TO SPECIFIC BANK ACCOUNT
def connect_to_my_bank(email, password):
    print("Client can connect to it's bank account")
def get_my_data_from_bank():
    print("Should obtain all the data from it's bank account (history,...) in JSON format")
def disconnect_from_my_bank():
    print("Should disconnect from the bank account")

## CLIENT FUNCTIONS
def create_category(category_name):
    print("Should create a new category")
def add_to_category(elt, category_name):
    print("Should add element to it's category")
def delete_category(category_name):
    print("Should delete the category")
def remove_from_category(elt, category_name):
    print("Should remove element from it's category")
def create_budget(category_name, amount_reached):
    print("Should create a new budget and notify if amount reached")
def remove_budget(budget_name):
    print("Should remove the budget")
def add_payment(amount, definition):
    print("Should add payment if not present in history of the bank")

#ACCESS TO APPLICATION DATABASE
def add_in_dataBase(elt):
    print("Can add entry in dataBase !")
def del_in_dataBase(elt):
    print("Can delete entry in dataBase !")
def get_in_dataBase(elt):
    print("Get element of dataBase!")

