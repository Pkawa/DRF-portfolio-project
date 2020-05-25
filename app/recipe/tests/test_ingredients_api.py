from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsAPITests(TestCase):
    """Test the publicly available ingredients API."""

    def setUp(self) -> None:
        self.client = APIClient()


class PrivateIngredientsAPITests(TestCase):
    """Test the private ingredients API."""

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            'test@user.com',
            'testpassword123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_login_required(self):
        self.client.force_authenticate(user=None, token=None)

        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_ingredients_list(self):
        """Test retrieving a list of ingredients."""
        Ingredient.objects.create(user=self.user, name='Mango')
        Ingredient.objects.create(user=self.user, name='Banana')

        # valid data for comparison
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        # api response
        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients only for the authenticated user are returned."""
        another_user = get_user_model().objects.create_user(
            email='another@user.com',
            password='SomePassword123'
        )
        # ingredient assigned to another user that we won't be abl to see
        Ingredient.objects.create(user=another_user, name='Papaya')
        # The only visible ingredient
        lime = Ingredient.objects.create(user=self.user, name='Lime')
        # api response
        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], lime.name)
