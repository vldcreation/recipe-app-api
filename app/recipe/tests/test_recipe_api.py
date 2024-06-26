"""
Test for the recipe APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from faker import Faker

from core.models import (
    Recipe,
    Tag,
)

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """Create and return a sample recipe"""
    faker = Faker()
    defaults = {
        'title': 'Sample recipe for ' + faker.word(),
        'time_minutes': 10,
        'price': Decimal('5.00'),
        'description': 'Sample description for recipe',
        'link': 'https://www.sample.com/recipe/1',
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test@123')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for user"""
        user2 = create_user(email='user2@example.com', password='test@123')
        create_recipe(user=user2)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test create recipe"""
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 20,
            'price': Decimal('10.00'),
            'description': 'Sample description',
            'link': 'https://www.sample.com/recipe/1',
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial update recipe"""
        original_link = 'https://www.sample.com/recipe/1'
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe',
            link=original_link,
        )

        payload = {
            'title': 'New title updated',
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update recipe"""
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe',
            link='https://www.sample.com/recipe/1',
            price=Decimal('10.00'),
            time_minutes=20,
            description='Sample description',
        )

        payload = {
            'title': 'New title updated',
            'time_minutes': 25,
            'price': Decimal('15.00'),
            'description': 'New description updated',
            'link': 'https://www.sample.com/recipe/2',
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test update recipe for other user returns error"""
        user2 = create_user(email='newuser@example.com', password='test@123')
        recipe = create_recipe(user=self.user)

        payload = {
            'user': user2,
        }

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test delete recipe"""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete other user recipe returns error"""
        user2 = create_user(
            email='user2@example.com',
            password='test@123',
        )
        recipe = create_recipe(user=user2)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_with_new_tags(self):
        """Test creating recipe with new tags"""
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 20,
            'price': Decimal('10.00'),
            'description': 'Sample description',
            'link': 'https://www.sample.com/recipe/1',
            'tags': [{'name': 'Vegan'}, {'name': 'Dessert'}]
        }

        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(res.data)

        recipe = Recipe.objects.get(id=res.data['id'])
        self.assertEqual(recipe.tags.count(), 2)

        for tag in payload['tags']:
            self.assertTrue(recipe.tags.filter(name=tag['name']).exists())

    def test_recipe_with_existing_tags(self):
        """Test creating recipe with existing tags"""
        tag1 = Tag.objects.create(user=self.user, name='Vegan')
        tag2 = Tag.objects.create(user=self.user, name='Dessert')

        payload = {
            'title': 'Sample recipe',
            'time_minutes': 20,
            'price': Decimal('10.00'),
            'description': 'Sample description',
            'link': 'https://www.sample.com/recipe/1',
            'tags': [
                {'name': tag1.name},
                {'name': tag2.name},
            ]
        }

        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(res.data)

        recipe = Recipe.objects.get(id=res.data['id'])
        self.assertEqual(recipe.tags.count(), 2)

        self.assertTrue(recipe.tags.filter(name=tag1.name).exists())
        self.assertTrue(recipe.tags.filter(name=tag2.name).exists())

    def create_tag_on_update(self):
        """Create tag when updating the recipe."""
        recipe = create_recipe(user=self.user)

        payload = {
            'title': 'New title updated',
            'tags': [{'name': 'Lunch'}],
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.tags.count(), 1)
        newTag = Tag.objects.get(user=self.user, name='Lunch')
        self.assertIn(newTag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating the recipe."""
        tagBreakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tagBreakfast)

        tagLunch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {'tags': [{'name': tagLunch.name}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(recipe.tags.count(), 1)
        self.assertIn(tagLunch, recipe.tags.all())

    def test_update_recipe_remove_tag(self):
        """Test removing an existing tag when updating the recipe."""
        tagBreakfast = Tag.objects.create(user=self.user, name='Breakfast')
        tagLunch = Tag.objects.create(user=self.user, name='Lunch')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tagBreakfast)
        recipe.tags.add(tagLunch)

        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tagBreakfast, recipe.tags.all())
        self.assertIn(tagLunch, recipe.tags.all())

        payload = {
            'title': 'New title updated',
            'tags': [],
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)
        self.assertNotIn(tagBreakfast, recipe.tags.all())
        self.assertNotIn(tagLunch, recipe.tags.all())
