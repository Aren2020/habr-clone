from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime
from users.models import User

class RegistrationTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'username': 'Ryan1980',
            'email': 'ryangosling@gmail.com',
            'first_name': 'Ryan',
            'last_name': 'Gosling',
            'password': '********',
        }

        self.invalid_data = {
            'email': 'mail.com',
            'first_name': False,
            'last_name': datetime(day = 12, month = 11, year = 1980),
        }
        self.url = reverse('users:registration')

    def test_valid_data(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username = self.valid_data['username']).exists())
        self.assertEqual(set(response.data), set(['access', 'refresh']))

    def test_invalid_data(self):
        response = self.client.post(self.url, self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class LoginTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'username': 'Ryan1980',
            'password': '********'
        }

        self.invalid_data = {
            'username': 'test',
            'password': 'test'
        }

        User.objects.create_user(**self.valid_data)
        self.url = reverse('users:login')

    def test_valid_data(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), set(['access', 'refresh']))

    def test_invalid_data(self):
        response = self.client.post(self.url, self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class LogoutTest(TestCase):
    def setUp(self):
        user = User.objects.create_user({
            'username': 'Ryan1980',
            'password': '********'
        })
        refresh = RefreshToken.for_user(user)
        refresh.payload.update({
            'user_id': user.id,
            'username': user.username
        })

        self.valid_token = str(refresh)
        self.invalid_token = 'invalid_refresh_token'
        self.url = reverse('users:logout')

    def test_valid_token(self):
        response = self.client.post(self.url, {'refresh_token': self.valid_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_token(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_token(self):
        response = self.client.post(self.url, {'refresh_token': self.invalid_token})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    