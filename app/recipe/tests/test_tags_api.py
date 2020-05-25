from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()


class PrivateTagsApiTests(TestCase):
    """Test authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@user.com',
            'testpassword123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(TAGS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Cycling')
        Tag.objects.create(user=self.user, name='Swimming')

        res = self.client.get(TAGS_URL)

        tags = list(Tag.objects.all().order_by('-name'))
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@user.com',
            'some_user'
        )

        Tag.objects.create(user=user2, name='Jogging')
        tag = Tag.objects.create(user=self.user, name='Vegan')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag."""
        payload = {'name': 'New tag'}
        response = self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid name."""
        payload = {'name': ''}
        response = self.client.post(TAGS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
