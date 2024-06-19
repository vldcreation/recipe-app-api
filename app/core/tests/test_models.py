"""Test for models"""
from decimal import Decimal  # noqa: F401

from django.test import TestCase
from django.contrib.auth import get_user_model
from faker import Faker

from core import models


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        fake = Faker()
        email = fake.email()
        password = fake.password()
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        sampleTests = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]

        for email, expected in sampleTests:
            user = get_user_model().objects.create_user(email, 'test123')

            self.assertEqual(user.email, expected)

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test@123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a new recipe is successful"""
        fake = Faker()
        email = fake.email()
        password = fake.password()
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.email, email)

        recipe = models.Recipe.objects.create(
            user=user,
            title='Steak and mushroom sauce',
            time_minutes=5,
            price=5.00,
            description='This is a test description'
        )

        self.assertIsNotNone(recipe)
        self.assertEqual(str(recipe), recipe.title)
