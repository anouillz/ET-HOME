class MockBank:
    def __init__(self, ):
        self.account = account

    def withdraw(self, amount, account):
        account.balance -= amount
        print(f"Withdrawn {amount}.- from {account.name}'s account.")

    def deposit(self, amount, account):
        account.balance += amount
        print(f"Deposit {amount}.- on {account.name}'s account.")

    def get_balance(self, account):
        print(f"Balance: {account.balance}")





class MockAccount:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance



#Mock data
account = MockAccount("Test1", 500)