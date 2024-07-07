from django.test import TestCase
from users.serializers import UserSerializer, UserEditSerializer, ChangePasswordSerializer
from datetime import datetime

class UserSerializerTest(TestCase):
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

    def test_valid_data(self):
        serializer = UserSerializer(data = self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_data(self):
        serializer = UserSerializer(data = self.invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['username', 'email', 'first_name',
                                                             'last_name', 'password']))
    
class UserEditSerializerTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'username': 'Ryan1980',
            'first_name': 'Ryan',
            'last_name': 'Gosling',
        }

        self.invalid_data = {
            'first_name': False,
            'last_name': datetime(day = 12, month = 11, year = 1980),
        }

    def test_valid_data(self):
        serializer = UserEditSerializer(data = self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_data(self):
        serializer = UserEditSerializer(data = self.invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['username', 'first_name', 'last_name']))

class ChangePasswordSerializerTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'old_password': '********',
            'new_password': '********'
        }

        self.invalid_data = {
            'old_password': datetime(day = 12, month = 11, year = 1980),
            'new_password': False
        }

    def test_valid_data(self):
        serializer = ChangePasswordSerializer(data = self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_data(self):
        serializer = ChangePasswordSerializer(data = self.invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), set(['old_password', 'new_password']))
        