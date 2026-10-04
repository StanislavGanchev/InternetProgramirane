from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from accounts.models import Profile

User = get_user_model()

PASSWORD = "Very-secret-123"


def registration_payload(**overrides):
    data = {
        "username": "player_one",
        "email": "player@example.com",
        "nickname": "MountainKnight",
        "password": PASSWORD,
        "password_confirm": PASSWORD,
    }
    data.update(overrides)
    return data


def make_user(username="knight", email="knight@example.com", nickname="SirKnight"):
    user = User.objects.create_user(username=username, email=email, password=PASSWORD)
    Profile.objects.create(user=user, nickname=nickname)
    return user


class RegistrationApiTests(APITestCase):
    url = reverse("accounts:register")

    def test_successful_registration(self):
        response = self.client.post(self.url, registration_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="player_one")
        self.assertEqual(user.profile.nickname, "MountainKnight")
        self.assertTrue(user.check_password(PASSWORD))
        self.assertNotIn("password", response.data)
        self.assertNotIn("password_confirm", response.data)
        self.assertEqual(
            response.data,
            {
                "id": user.id,
                "username": "player_one",
                "email": "player@example.com",
                "profile": {"nickname": "MountainKnight", "avatar_key": "knight-1"},
            },
        )

    def test_invalid_registration(self):
        make_user(username="taken", email="taken@example.com", nickname="TakenNick")
        cases = [
            ("username", {"username": "taken"}),
            ("email", {"email": "taken@example.com"}),
            ("nickname", {"nickname": "TakenNick"}),
            ("password_confirm", {"password_confirm": "Different-123"}),
        ]
        for field, overrides in cases:
            with self.subTest(field=field):
                users_before = User.objects.count()
                response = self.client.post(
                    self.url, registration_payload(**overrides), format="json"
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data["errors"])
                self.assertEqual(User.objects.count(), users_before)


class SessionApiTests(APITestCase):
    login_url = reverse("accounts:login")
    logout_url = reverse("accounts:logout")
    me_url = reverse("accounts:me")

    def setUp(self):
        self.user = make_user()

    def test_successful_login_creates_session(self):
        response = self.client.post(
            self.login_url, {"username": "knight", "password": PASSWORD}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("sessionid", response.cookies)

        me = self.client.get(self.me_url)
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["id"], self.user.id)
        self.assertEqual(me.data["username"], "knight")

    def test_failed_login(self):
        response = self.client.post(
            self.login_url, {"username": "knight", "password": "wrong"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)
        self.assertNotIn("sessionid", response.cookies)

        me = self.client.get(self.me_url)
        self.assertIn(me.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_me_permissions(self):
        anonymous = self.client.get(self.me_url)
        self.assertIn(
            anonymous.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
        )

        make_user(username="other", email="other@example.com", nickname="OtherNick")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "knight")
        self.assertEqual(response.data["profile"]["nickname"], "SirKnight")

    def test_profile_update(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            self.me_url,
            {"nickname": "NewKnight", "avatar_key": "knight-3", "is_staff": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["profile"]["nickname"], "NewKnight")

        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.nickname, "NewKnight")
        self.assertEqual(self.user.profile.avatar_key, "knight-3")
        self.assertFalse(self.user.is_staff)

    def test_logout_ends_session(self):
        self.client.post(
            self.login_url, {"username": "knight", "password": PASSWORD}, format="json"
        )
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        me = self.client.get(self.me_url)
        self.assertIn(me.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))


class CsrfApiTests(APITestCase):
    def test_unsafe_request_requires_csrf_token(self):
        make_user()
        client = APIClient(enforce_csrf_checks=True)

        csrf_response = client.get(reverse("accounts:csrf"))
        self.assertEqual(csrf_response.status_code, status.HTTP_204_NO_CONTENT)
        token = client.cookies["csrftoken"].value

        login = client.post(
            reverse("accounts:login"),
            {"username": "knight", "password": PASSWORD},
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value  # rotated on login

        payload = {"nickname": "CsrfKnight"}
        without_token = client.patch(reverse("accounts:me"), payload, format="json")
        self.assertEqual(without_token.status_code, status.HTTP_403_FORBIDDEN)

        with_token = client.patch(
            reverse("accounts:me"), payload, format="json", HTTP_X_CSRFTOKEN=token
        )
        self.assertEqual(with_token.status_code, status.HTTP_200_OK)
        self.assertEqual(with_token.data["profile"]["nickname"], "CsrfKnight")
