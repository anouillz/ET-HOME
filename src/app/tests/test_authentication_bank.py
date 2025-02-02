import unittest
import json
from django.test import TestCase, Client
from django.urls import reverse
from bank.models import BankAccount, Secret, Client



class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here


    def setUp(self):
        # Create a test client
        self.client = Client()

        # Create a test user
        self.user = Client.objects.create_user(
            username='testuser',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )

        # Create a test bank account
        self.bank_account = BankAccount.objects.create(
            user=self.user,
            account_number='1234567890',
            balance=1000.0,
            bank_name='Test Bank'
        )

    def test_generate_secret(self):
        # Log in the test user
        self.client.login(username='testuser', password='testpassword')

        # Send a POST request to generate a secret
        response = self.client.post(reverse('generate_secret'), {
            'user_id': self.user.id,
            'password': 'testpassword',
            'account_number': self.bank_account.account_number
        })

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check that the response contains the secret and its ID
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        self.assertIn('secret', response_data)
        self.assertIn('id', response_data)

        # Check that the secret was created in the database
        secret = Secret.objects.get(id=response_data['id'])
        self.assertEqual(secret.account, self.bank_account)
        self.assertEqual(secret.code, response_data['secret'])


if __name__ == '__main__':
    unittest.main()
