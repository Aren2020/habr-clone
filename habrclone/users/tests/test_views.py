from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from datetime import datetime
from unittest import mock
from users.models import User, PasswordReset

class RegistrationTest(APITestCase):
    
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

class LoginTest(APITestCase):
    
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

class LogoutTest(APITestCase):
    
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
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_no_token(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_token(self):
        response = self.client.post(self.url, {'refresh_token': self.invalid_token})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class EditTest(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username = 'Ryan1980',
            password = '********'
        )
        access_token = AccessToken.for_user(self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        self.valid_data = {
            'username': 'Ryan1980',
            'first_name': 'Ryan',
            'last_name': 'Gosling',
        }

        self.invalid_data = {
            'first_name': False,
            'last_name': datetime(day = 12, month = 11, year = 1980),
        }

        self.url = reverse('users:edit')

    def test_get_method(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), set(['username', 'first_name', 'last_name']))

    def test_valid_data(self):
        response = self.client.patch(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user = User.objects.get(pk = self.user.pk)
        for field, value in self.valid_data.items():
            self.assertEqual(getattr(user, field), value)

    def test_invalid_data(self):
        response = self.client.patch(self.url, self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class CodeEmailTest(APITestCase):

    @mock.patch('users.views.verification_mail.delay')
    def test_post_request_sends_email(self, mock_verification_mail):
        mock_verification_mail.return_value = None

        url = reverse('users:verify')
        data = {
            'username': 'Ryan1980',
            'first_name': 'Ryan',
            'last_name': 'Gosling',
            'email': 'RyanGosling@gmail.com'
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('code', response.data)

        mock_verification_mail.assert_called_once_with(
            data['username'], f'{data["first_name"]} {data["last_name"]}', data['email'], mock.ANY
        )

        returned_code = response.data['code']
        self.assertTrue(isinstance(returned_code, int))
        self.assertTrue(100000 <= returned_code <= 1000000)

class ChangePasswordTest(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username = 'Ryan1980',
            password = '********'
        )
        self.user_pk = self.user.pk
        access_token = AccessToken.for_user(self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        self.valid_data = {
            'old_password': '********',
            'new_password': 'Ryan1980'
        }

        self.wrong_password = {
            'old_password': 'Ryan1980',
            'new_password': 'Ryan1980'
        }

        self.invalid_data = {
            'old_password': '********',
        }

        self.url = reverse('users:password_change')
    
    def test_valid_data(self):
        response = self.client.patch(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        user = User.objects.get(pk = self.user_pk)
        new_password = self.valid_data['new_password']
        self.assertTrue( user.check_password( new_password ))

    def test_wrong_password(self):
        response = self.client.patch(self.url, self.wrong_password)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_data(self):
        response = self.client.patch(self.url, self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class PasswordResetTest(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username = 'Ryan1980',
            first_name = 'Ryan',
            last_name = 'Gosling',
            email = 'RyanGosling@gmail.com',
            password = '********'
        )

        self.invalid_data = {
            'email': 'Ryan1980'
        }
    
        self.url = reverse('users:password_reset')

    @mock.patch('users.views.password_reset_mail.delay')
    def test_valid_data(self, mock_password_reset_mail):
        response = self.client.post(self.url, {'email': self.user.email})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        mock_password_reset_mail.assert_called_once_with(
            self.user.username, f'{self.user.first_name} {self.user.last_name}', self.user.email, mock.ANY
        )
        

    def test_invalid_data(self):
        response = self.client.post(self.url, self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class PasswordResetDoneTest(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username = 'Ryan1980',
            first_name = 'Ryan',
            last_name = 'Gosling',
            email = 'RyanGosling@gmail.com',
            password = '********'
        )
        token_generator = PasswordResetTokenGenerator()
        self.token = token_generator.make_token(self.user)
        reset = PasswordReset(email = self.user.email, token = self.token)
        reset.save()

        self.valid_token = reverse('users:password_reset_done',  args = [self.token])
        self.invalid_token = reverse('users:password_reset_done',  args = ['invalid_token'])

    def test_valid_url(self):
        response = self.client.post(self.valid_token, {'password': 'Ryan1980'})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user = User.objects.get(username = self.user.username)
        self.assertTrue(user.check_password('Ryan1980'))
    
    def test_invalid_url(self):
        response = self.client.post(self.invalid_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)