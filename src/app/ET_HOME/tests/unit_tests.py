import json
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.auth import get_user_model
from ET_HOME.models import SpendingCategory
from ET_HOME import views
from ET_HOME.api_views import change_password
from ET_HOME.models import Notification, NotificationType

User = get_user_model()

# needed for login tests
def attach_middleware(request):
    # Add session support
    session_middleware = SessionMiddleware(get_response=lambda r: None)
    session_middleware.process_request(request)
    request.session.save()

    # Add messages support
    messages_middleware = MessageMiddleware(get_response=lambda r: None)
    messages_middleware.process_request(request)

    return request

# testing login
class LoginViewUnitTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        # Create a user for login tests
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass"
        )

    def test_login_success(self):
        request = self.factory.post('/login/', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        request.user = AnonymousUser()
        request = attach_middleware(request)

        response = views.login_view(request)
        # Expect a redirect (status code 302) to the dashboard
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard"))

    def test_login_fail(self):
        request = self.factory.post('/login/', data={
            'username': 'testuser',
            'password': 'wrongpass'
        })
        request.user = AnonymousUser()
        request = attach_middleware(request)

        response = views.login_view(request)
        # Expect the login page to be re-rendered with an error message.
        self.assertEqual(response.status_code, 200)
        self.assertIn("Invalid username or password", response.content.decode())

    def test_logout(self):
        request = self.factory.get('/logout/')
        request.user = self.user
        request = attach_middleware(request)

        response = views.logout_view(request)
        # Expect a redirect (status code 302) to the login page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))

# testing registration
class RegistrationViewUnitTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_register_and_default_categories(self):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "testpass",
            "firstname": "New",
            "lastname": "User",
        }
        request = self.factory.post('/register/', data=data)
        request.user = AnonymousUser()

        response = views.register_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))

        # Verify the user was created.
        user = User.objects.get(username="newuser")
        self.assertEqual(user.email, "newuser@example.com")

        # Verify that 6 default spending categories were created.
        categories = SpendingCategory.objects.filter(user=user)
        self.assertEqual(categories.count(), 6)


# categories unit tests
class CategoryViewUnitTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        # Create a non-default category.
        self.category = SpendingCategory.objects.create(
            name="Food", user=self.user, is_default=False, user_budget=100.00
        )

    def test_categories_view_authenticated(self):
        request = self.factory.get('/categories/')
        request.user = self.user

        response = views.categories_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Food", response.content.decode())

    def test_categories_view_requires_login(self):
        request = self.factory.get('/categories/')
        request.user = AnonymousUser()

        response = views.categories_view(request)
        # redirects unauthenticated users to the login page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))


# navigation unit tests
class NavigationViewUnitTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="testpass")

    def test_dashboard_access(self):
        request = self.factory.get('/dashboard/')
        request.user = self.user

        response = views.dashboard_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user.username, response.content.decode())

    def test_settings_access(self):
        request = self.factory.get('/settings/')
        request.user = self.user

        response = views.settings_view(request)
        self.assertEqual(response.status_code, 200)

    def test_account_access(self):
        request = self.factory.get('/account/')
        request.user = self.user

        response = views.account_view(request)
        self.assertEqual(response.status_code, 200)

    def test_transactions_access(self):
        request = self.factory.get('/transactions/')
        request.user = self.user

        response = views.transactions_view(request)
        self.assertEqual(response.status_code, 200)


# change password tests
class ChangePasswordUnitTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        # Create a test user with password 'oldpass'
        self.user = User.objects.create_user(username="testuser", password="oldpass")
        self.user.save()

    # test missing fields
    def test_missing_fields(self):

        request = self.factory.post('/dummy-url/', data={})
        request.user = self.user
        request = attach_middleware(request)

        response = change_password(request)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data.get("status"), "error")
        self.assertEqual(data.get("error"), "All fields are required")

    # test new password mismatch
    def test_new_password_mismatch(self):
        data = {
            "current_password": "oldpass",
            "new_password": "newpass",
            "confirm_password": "different"
        }
        request = self.factory.post('/dummy-url/', data=data)
        request.user = self.user
        request = attach_middleware(request)

        response = change_password(request)
        self.assertEqual(response.status_code, 400)
        data_response = json.loads(response.content)
        self.assertEqual(data_response.get("status"), "error")
        self.assertEqual(data_response.get("error"), "New password and confirmation do not match")

    # test incorrect current password
    def test_incorrect_current_password(self):
        data = {
            "current_password": "wrongpass",
            "new_password": "newpass",
            "confirm_password": "newpass"
        }
        request = self.factory.post('/dummy-url/', data=data)
        request.user = self.user
        request = attach_middleware(request)

        response = change_password(request)
        self.assertEqual(response.status_code, 400)
        data_response = json.loads(response.content)
        self.assertEqual(data_response.get("status"), "error")
        self.assertEqual(data_response.get("error"), "Current password is incorrect")

    # test successful password change
    def test_change_password_success(self):
        data = {
            "current_password": "oldpass",
            "new_password": "newpass",
            "confirm_password": "newpass"
        }
        request = self.factory.post('/dummy-url/', data=data)
        request.user = self.user
        request = attach_middleware(request)

        response = change_password(request)
        self.assertEqual(response.status_code, 200)
        data_response = json.loads(response.content)
        self.assertEqual(data_response.get("status"), "success")

        # Refresh the user from the DB and verify the password was changed.
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass"))

        # Verify that a notification was created.
        self.assertTrue(
            Notification.objects.filter(
                user=self.user,
                type=NotificationType.GENERAL,
                message="Successfully changed password"
            ).exists()
        )
