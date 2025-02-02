from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth import get_user_model

import time

class SystemTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Initialize the webdriver (adjust the executable_path if needed)
        cls.selenium = webdriver.Chrome()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        # Create a test user (using your project's user model)
        User = get_user_model()
        self.test_username = "systemuser"
        self.test_password = "systempass"
        User.objects.create_user(username=self.test_username, password=self.test_password)

    def test_homepage_contains_dashboard_link(self):
        # 1. Navigate to the login page.
        login_url = self.live_server_url + reverse("login")
        self.selenium.get(login_url)

        # 2. Fill in the login form.
        username_input = self.selenium.find_element(By.NAME, "username")
        password_input = self.selenium.find_element(By.NAME, "password")
        username_input.send_keys(self.test_username)
        password_input.send_keys(self.test_password)
        password_input.send_keys(Keys.RETURN)

        # 3. Wait until redirected to the dashboard or a page that contains a "Dashboard" link.
        try:
            dashboard_link = WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Dashboard"))
            )
        except Exception as e:
            self.fail("Dashboard link was not found after login.")

        # 4. Assert that the Dashboard link exists.
        self.assertIsNotNone(dashboard_link)
        # Optionally, click the Dashboard link and verify that the dashboard loads.
        dashboard_link.click()
        time.sleep(2)  # Consider using explicit waits for a production test.
        self.assertIn("Dashboard", self.selenium.title)
