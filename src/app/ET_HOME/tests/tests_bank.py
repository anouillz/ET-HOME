import json
import uuid
import secrets
import hmac
from datetime import timedelta, datetime

from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.utils.timezone import now
from django.middleware.csrf import get_token
from unittest.mock import patch, MagicMock

# Import models and views from bank app
from bank.models import (
    Client as BankClient,
    BankAccount,
    Secret,
    Token,
    Transaction,
    SpendingCategory
)
from bank import views as bank_views
from bank.middlewares import check_token_validity

# Import ET_HOME modules
from ET_HOME.core import bank_auth
from ET_HOME.models import User, BankAccount as ETBankAccount, AppToken
from ET_HOME import views as et_home_views

################################################################################
# Tests for the bank app (models, middleware, and views)
################################################################################

class TestBankViews(TestCase):
    databases = {"default", "db_bank"}

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        # Create a user using the bank’s Client model.
        self.user = BankClient.objects.create_user(username="testuser", password="testpass")
        # Create a bank account (from bank.models) for this user.
        self.account = BankAccount.objects.create(
            user=self.user,
            account_number="12345678",
            balance=1000.00,
            bank_name="Test Bank"
        )
        # Create a secret for the account.
        self.secret = Secret.objects.create(
            account=self.account,
            code=secrets.token_hex(64)  # 128 hex characters
        )
        # Create a valid token (activated and not expired).
        self.token = Token.objects.create(
            id=uuid.uuid4(),
            code=secrets.token_hex(64),
            account=self.account,
            secret=self.secret,
            created_at=now(),
            expires_at=now() + timedelta(hours=1),
            activated=True,
            challenge="abcdef1234567890abcdef1234567890"
        )
        # Create a spending category.
        self.category = SpendingCategory.objects.create(
            name="Food",
            user=self.user
        )
        # Create a transaction.
        self.transaction = Transaction.objects.create(
            account=self.account,
            amount=50.00,
            description="Test transaction",
            category=self.category
        )
        # Prepare a valid HTTP_AUTHORIZATION header.
        self.auth_header = "Bearer " + self.token.code

    def test_get_transaction_success(self):
        url = reverse("bank:get_transaction", args=[str(self.transaction.id)])
        request = self.factory.get(url, HTTP_AUTHORIZATION=self.auth_header)
        # Normally, the token_protected decorator sets request.account.
        # For testing, we simulate that.
        request.account = self.account
        response = bank_views.get_transaction(request, self.transaction.id)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["description"], "Test transaction")

    def test_get_transactions_success(self):
        url = reverse("bank:get_transactions")
        request = self.factory.get(url, HTTP_AUTHORIZATION=self.auth_header)
        request.account = self.account
        response = bank_views.get_transactions(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "success")
        # At least one transaction should be returned.
        self.assertTrue(len(data["data"]) >= 1)

    def test_filter_transaction_success(self):
        url = reverse("bank:filter_transaction")
        payload = {
            "start_date": now().isoformat(),
            "end_date": now().isoformat(),
            "categories": [str(self.category.id)]
        }
        request = self.factory.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.auth_header
        )
        request.account = self.account
        response = bank_views.filter_transaction(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "success")

    def test_get_account_success(self):
        url = reverse("bank:get_account")
        request = self.factory.get(url, HTTP_AUTHORIZATION=self.auth_header)
        request.account = self.account
        response = bank_views.get_account(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["account_number"], self.account.account_number)

    def test_generate_secret_success(self):
        url = reverse("bank:gen_secret")
        # POST request with account_number and password.
        request = self.factory.post(url, data={
            "account_number": self.account.account_number,
            "password": "testpass"
        })
        response = bank_views.generate_secret(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "success")
        self.assertIn("secret", data)
        self.assertIn("id", data)

    def test_generate_token_challenge(self):
        url = reverse("bank:gen_token")
        # First call without token_id should return a challenge.
        request = self.factory.post(url, data={
            "account_number": self.account.account_number,
            "secret_id": str(self.secret.id)
        })
        response = bank_views.generate_token(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "success")
        self.assertIn("challenge", data)
        self.assertIn("token_id", data)

    def test_add_transaction_success(self):
        url = reverse("bank:add_transaction")
        request = self.factory.post(url, data={
            "account_id": str(self.account.id),
            "category_id": str(self.category.id),
            "amount": "75.00",
            "description": "New transaction"
        })
        response = bank_views.add_transaction(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "success")
        self.assertIn("id", data)

    def test_add_account_success(self):
        url = reverse("bank:add_account")
        request = self.factory.post(url, data={
            "account_number": "87654321",
            "balance": "500.00",
            "bank_name": "Test Bank 2",
            "user_id": str(self.user.id)
        })
        response = bank_views.add_account(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "success")
        self.assertIn("id", data)

    def test_add_category_success(self):
        url = reverse("bank:add_category")
        request = self.factory.post(url, data={"name": "Utilities"})
        response = bank_views.add_category(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "success")
        self.assertIn("id", data)


class TestBankMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        # Create a user and associated bank account, secret, and token.
        self.user = BankClient.objects.create_user(username="middlewareuser", password="testpass")
        self.account = BankAccount.objects.create(
            user=self.user,
            account_number="99999999",
            balance=1000.00,
            bank_name="Middleware Bank"
        )
        self.secret = Secret.objects.create(
            account=self.account,
            code=secrets.token_hex(64)
        )
        self.token = Token.objects.create(
            id=uuid.uuid4(),
            code=secrets.token_hex(64),
            account=self.account,
            secret=self.secret,
            created_at=now(),
            expires_at=now() + timedelta(hours=1),
            activated=True,
            challenge="abcdef1234567890abcdef1234567890"
        )

    def test_check_token_validity_success(self):
        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = "Bearer " + self.token.code
        valid = check_token_validity(request)
        self.assertTrue(valid)
        self.assertEqual(request.account, self.account)

    def test_check_token_validity_failure(self):
        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = "Bearer invalidtoken"
        valid = check_token_validity(request)
        self.assertFalse(valid)


################################################################################
# Tests for ET_HOME/core/bank_auth functions (which call external endpoints)
################################################################################

class TestETHomeBankAuth(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        # Create a dummy ET_HOME user (using your custom User model)
        self.user = User.objects.create_user(username="etuser", password="etpass", email="et@example.com")
        # Create an ET_HOME bank account
        self.et_account = ETBankAccount.objects.create(
            user=self.user,
            account_number="ET123456",
            balance=1000.00,
            bank_name="ET Bank",
            secret="dummysecret",
            secret_id=uuid.uuid4()
        )
        # For our tests, we assume bank_auth.make_new_token uses the generate_token function.
        # We won’t simulate the full challenge process; instead we’ll patch requests.
        self.factory = RequestFactory()

    @patch("ET_HOME.core.bank_auth.requests.post")
    def test_generate_secret_et_home(self, mock_post):
        request = self.factory.post("/")
        csrf_token = get_token(request)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "status": "success",
            "secret": "dummysecretvalue",
            "id": "1234-5678"
        }
        mock_post.return_value = mock_resp
        res = bank_auth.generate_secret(request, "ET123456", "etpass")
        self.assertIsNotNone(res)
        self.assertEqual(res["secret"], "dummysecretvalue")

    @patch("ET_HOME.core.bank_auth.requests.post")
    def test_generate_token_et_home(self, mock_post):
        request = self.factory.post("/")
        csrf_token = get_token(request)
        # First call returns a challenge.
        challenge = "abcdef1234567890abcdef1234567890"
        token_id = str(uuid.uuid4())
        mock_resp_challenge = MagicMock()
        mock_resp_challenge.status_code = 200
        mock_resp_challenge.json.return_value = {
            "status": "success",
            "challenge": challenge,
            "token_id": token_id
        }
        # Second call returns token details.
        mock_resp_validation = MagicMock()
        mock_resp_validation.status_code = 200
        mock_resp_validation.json.return_value = {
            "status": "success",
            "token": {
                "id": str(uuid.uuid4()),
                "code": "et_token_code",
                "expires_at": (now() + timedelta(hours=1)).isoformat()
            }
        }
        mock_post.side_effect = [mock_resp_challenge, mock_resp_validation]
        token_data, err = bank_auth.generate_token(request, "ET123456", "dummysecret", "dummy-secret-id")
        self.assertIsNone(err)
        self.assertIsNotNone(token_data)
        self.assertEqual(token_data["code"], "et_token_code")


################################################################################
# Tests for ET_HOME/views (authentication and template-based views)
################################################################################

class TestETHomeViews(TestCase):
    def setUp(self):
        self.client = Client()
        # Create an ET_HOME user (your custom User model from ET_HOME/models)
        self.user = User.objects.create_user(username="etviewuser", password="etviewpass", email="etview@example.com")
        # Log in the user.
        self.client.login(username="etviewuser", password="etviewpass")

    def test_dashboard_view(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("dashboard.html", [t.name for t in response.templates])

    def test_register_view_get(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("register.html", [t.name for t in response.templates])

    def test_login_view_get(self):
        # Logout first to test login view.
        self.client.logout()
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("login.html", [t.name for t in response.templates])
