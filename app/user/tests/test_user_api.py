from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


# endpoints that do not require authentication
class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'email': 'example@user.com',
            'password': 'examplepassword',
            'name': 'Example User'
        }

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password']))
        # making sure password is never returned in the response
        self.assertNotIn('password', response.data)

    def test_user_exists(self):
        """Test creating an user that already exists fails"""
        payload = {
            'email': 'example@user.com',
            'password': 'examplepassword',
            'name': 'Example User'
        }

        create_user(**payload)
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the passwordm u be more than 5 characters."""
        payload = {
            'email': 'example@user.com',
            'password': 'expw',
            'name': 'Example User'
        }

        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        payload = {
            'email': 'example@user.com',
            'password': 'examplepassword',
            'name': 'Example User'
        }

        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Token is not created if invalid credentials are passed."""
        payload = {
            'email': 'example@user.com',
            'password': 'examplepassword',
            'name': 'Example User'
        }

        create_user(**payload)
        payload['password'] = 'Wrong password'
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user does not exist."""
        response = self.client.post(TOKEN_URL, {'email': 'w', 'password': 'w'})

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PrivateUserApiTests(TestCase):

    def setUp(self):
        self.user = create_user(
            email='example@user.com',
            password='examplepassword',
            name='Example User'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_profile_unauthorized(self):
        """Test that authentication is required for users."""
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_user_profile_success(self):
        """Test retrieving user profile for logged in users."""
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on me url."""
        response = self.client.post(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
