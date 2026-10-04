from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from accounts.models import Profile

User = get_user_model()


class UserAndProfileModelTests(TestCase):
    def test_create_user_hashes_password_and_links_profile(self):
        user = User.objects.create_user(
            username="knight", email="knight@example.com", password="Str0ng-pass!"
        )
        profile = Profile.objects.create(user=user, nickname="SirKnight")

        self.assertNotEqual(user.password, "Str0ng-pass!")
        self.assertTrue(user.check_password("Str0ng-pass!"))
        self.assertEqual(user.profile, profile)
        self.assertEqual(profile.avatar_key, "knight-1")

    def test_email_must_be_unique(self):
        User.objects.create_user(username="a", email="same@example.com", password="x")
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username="b", email="same@example.com", password="x")

    def test_nickname_must_be_unique(self):
        first = User.objects.create_user(username="a", email="a@example.com", password="x")
        second = User.objects.create_user(username="b", email="b@example.com", password="x")
        Profile.objects.create(user=first, nickname="Dup")
        with self.assertRaises(IntegrityError):
            Profile.objects.create(user=second, nickname="Dup")
