
from django.test import TestCase, Client
from django.urls import reverse
from ..models import (
    Notification,
    NotificationType,
    Transaction,
    SpendingCategory,
    User
)

# User authentication tests
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

# User registration tests
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

# Category view tests
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

# Navigation tests
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

# Notification tests
class NotificationEndpointTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a user and log in
        self.user = User.objects.create_user(username="notifuser", password="testpass")
        self.client.login(username="notifuser", password="testpass")

    # if no notifications, endpoint should return empty list
    def test_get_notifications_empty(self):
        response = self.client.get(reverse("api:get_notifications"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "success")
        self.assertEqual(len(data.get("notifications", [])), 0)

    # if there is a notification, endpoint should return it
    def test_get_notifications_with_notification(self):
        Notification.objects.create(
            user=self.user,
            type=NotificationType.GENERAL,
            message="Test Notification"
        )
        response = self.client.get(reverse("api:get_notifications"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "success")
        self.assertEqual(len(data.get("notifications", [])), 1)
        self.assertEqual(data["notifications"][0]["message"], "Test Notification")

    # test reading a notification
    def test_read_notification(self):

        notif = Notification.objects.create(
            user=self.user,
            type=NotificationType.GENERAL,
            message="Please read this"
        )
        url = reverse("api:read_notification", args=[notif.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "success")
        # Refresh the notification from the database and verify it is marked as read.
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)

# Transaction tests
class TransactionEndpointTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="transuser", password="testpass")
        self.client.login(username="transuser", password="testpass")
        # create a spending category used by transactions.
        self.category = SpendingCategory.objects.create(
            user=self.user,
            name="Groceries",
            user_budget=100,
            is_default=False,
            trigger_notification=False
        )

    # test adding a transaction
    def test_add_transaction_success(self):
        data = {
            "category_id": str(self.category.id),
            "amount": "50.00",
            "date": "2020-01-15",
            "description": "Weekly groceries"
        }
        response = self.client.post(reverse("api:add_transactions"), data=data)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data.get("status"), "success")
        self.assertIn("transaction", json_data)

        # Check that the transaction is created in the database.
        transaction_id = json_data["transaction"].get("id")
        transaction = Transaction.objects.get(id=transaction_id)
        self.assertEqual(str(transaction.category.id), str(self.category.id))
        self.assertEqual(str(transaction.amount), "50.00")
        self.assertEqual(transaction.description, "Weekly groceries")

    # test adding a transaction with missing fields -> error
    def test_add_transaction_missing_fields(self):
        # Missing 'description'
        data = {
            "category_id": str(self.category.id),
            "amount": "50.00",
            "date": "2020-01-15",
        }
        response = self.client.post(reverse("api:add_transactions"), data=data)
        # Expecting an error status code (e.g. 400)
        self.assertEqual(response.status_code, 400)
        json_data = response.json()
        self.assertEqual(json_data.get("status"), "error")

    # test getting transactions with no bank account
    def test_transaction_api_get_post_delete_without_account(self):
        # Create a transaction without an account.
        transaction = Transaction.objects.create(
            user=self.user,
            amount=75,
            date="2020-02-15",
            description="Test Transaction API",
            category=self.category
        )
        url = reverse("api:transaction_api", args=[transaction.id])

        # Test GET request.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data.get("status"), "success")
        self.assertIn("transaction", json_data)

        # Test POST to update the transaction.
        update_data = {
            "amount": "85.00",
            "date": "2020-02-16",
            "category_id": str(self.category.id),
            "description": "Updated Transaction"
        }
        response = self.client.post(url, data=update_data)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data.get("status"), "success")
        updated_transaction = Transaction.objects.get(id=transaction.id)
        self.assertEqual(str(updated_transaction.amount), "85.00")
        self.assertEqual(updated_transaction.description, "Updated Transaction")

        # Test DELETE to remove the transaction.
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data.get("status"), "success")
        with self.assertRaises(Transaction.DoesNotExist):
            Transaction.objects.get(id=transaction.id)

