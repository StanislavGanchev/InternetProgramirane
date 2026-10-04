from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import Profile
from accounts.serializers import ProfileUpdateSerializer, RegisterSerializer

User = get_user_model()

VALID_DATA = {
    "username": "player_one",
    "email": "player@example.com",
    "nickname": "MountainKnight",
    "password": "Very-secret-123",
    "password_confirm": "Very-secret-123",
}


class RegisterSerializerTests(TestCase):
    def test_valid_data_creates_user_and_profile(self):
        serializer = RegisterSerializer(data=VALID_DATA)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertTrue(user.check_password(VALID_DATA["password"]))
        self.assertEqual(user.profile.nickname, "MountainKnight")
        self.assertNotIn("password", serializer.data)
        self.assertNotIn("password_confirm", serializer.data)

    def test_password_mismatch_is_rejected(self):
        data = {**VALID_DATA, "password_confirm": "Something-else-1"}
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password_confirm", serializer.errors)


class ProfileUpdateSerializerTests(TestCase):
    def test_only_allowed_fields_are_changed(self):
        user = User.objects.create_user(username="u", email="u@example.com", password="x")
        profile = Profile.objects.create(user=user, nickname="Old")

        serializer = ProfileUpdateSerializer(
            profile,
            data={"nickname": "New", "avatar_key": "knight-2", "is_staff": True},
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        profile.refresh_from_db()
        user.refresh_from_db()
        self.assertEqual(profile.nickname, "New")
        self.assertEqual(profile.avatar_key, "knight-2")
        self.assertFalse(user.is_staff)

    def test_invalid_avatar_is_rejected(self):
        user = User.objects.create_user(username="u", email="u@example.com", password="x")
        profile = Profile.objects.create(user=user, nickname="Old")
        serializer = ProfileUpdateSerializer(
            profile, data={"avatar_key": "dragon-9"}, partial=True
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("avatar_key", serializer.errors)
