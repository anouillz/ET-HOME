from django.test import TestCase, Client
from django.urls import reverse
from .models import SpendingCategory, Transaction, User

class UserAuthTests(TestCase):
    def setUp(self):
        # create user for testing
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass")
        self.client = Client()  # django client for simulation

    def test_login_success(self):
        # test successful login
        response = self.client.post(reverse("login"), {"username": "testuser", "password": "testpass"})
        self.assertRedirects(response, reverse("dashboard"))

    def test_login_fail(self):
        # test failed login (wrong password)
        response = self.client.post(reverse("login"), {"username": "testuser", "password": "wrongpass"})
        self.assertEqual(response.status_code, 200)  # login page should be reloaded
        self.assertContains(response, "Invalid username or password")

    def test_logout(self):
        # test logout
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, reverse("login"))

class RegistrationTests(TestCase):
    def test_register_and_default_categories(self):
        # test registration and default categories creation
        response = self.client.post(reverse("register"), {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "testpass",
            "firstname": "New",
            "lastname": "User",
        })
        self.assertRedirects(response, reverse("login"))

        # check if user is created
        user = User.objects.get(username="newuser")
        self.assertEqual(user.email, "newuser@example.com")

        # check if default categories are created
        categories = SpendingCategory.objects.filter(user=user)
        self.assertEqual(categories.count(), 6) # 6 default categories

class CategoryViewTests(TestCase):
    def setUp(self):
        # create user with personal category
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")
        self.category = SpendingCategory.objects.create(name="Food", user=self.user, is_default=False, user_budget=100.00)

    def test_categories_view(self):
        # test categories view
        response = self.client.get(reverse("categories"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Food")

    def test_categories_requires_login(self):
        # test categories view requires login
        self.client.logout()
        response = self.client.get(reverse("categories"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('categories')}")

class NavigationTests(TestCase):
    def setUp(self):
        # create user and login
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

    def test_dashboard_access(self):
        # test dashboard access
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)

    def test_settings_access(self):
        # test settings access
        response = self.client.get(reverse("settings"))
        self.assertEqual(response.status_code, 200)

    def test_account_access(self):
        # test account access
        response = self.client.get(reverse("account"))
        self.assertEqual(response.status_code, 200)

class TransactionViewTests(TestCase):
    def setUp(self):
        # create user for transactions
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        # TODO create account and transactions

    def test_transactions_view(self):
        # test transactions view
        response = self.client.get(reverse("transactions"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test transaction")
