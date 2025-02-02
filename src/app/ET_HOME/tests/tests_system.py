from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth import get_user_model
from selenium.common.exceptions import NoAlertPresentException, UnexpectedAlertPresentException
import time


class SystemTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # initiate webdriver for Chrome
        cls.selenium = webdriver.Chrome()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        # create test user
        User = get_user_model()
        self.test_username = "systemuser"
        self.test_password = "systempass"
        User.objects.create_user(username=self.test_username, password=self.test_password)

    def test_homepage_contains_dashboard_link(self):
        # login page
        login_url = self.live_server_url + reverse("login")
        self.selenium.get(login_url)

        # log in the app with test user
        username_input = self.selenium.find_element(By.NAME, "username")
        password_input = self.selenium.find_element(By.NAME, "password")
        username_input.send_keys(self.test_username)
        password_input.send_keys(self.test_password)
        password_input.send_keys(Keys.RETURN)

        # wait for dashboard access
        try:
            dashboard_link = WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Dashboard"))
            )
        except Exception as e:
            self.fail("Dashboard link not found")

        # check if dashboard link is present
        self.assertIsNotNone(dashboard_link)

        # click on dashboard link
        dashboard_link.click()

        # manage eventual alert
        try:
            WebDriverWait(self.selenium, 5).until(EC.alert_is_present())
            alert = self.selenium.switch_to.alert
            print("Alerte détectée :", alert.text)
            alert.accept()
        except (NoAlertPresentException, UnexpectedAlertPresentException):
            pass

        # wait for page to load
        time.sleep(2)
        self.assertIn("Dashboard", self.selenium.title)
