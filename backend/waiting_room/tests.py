from django.contrib.auth import get_user_model
from django.test import TestCase

from games.models import Game, GamePlayer, Round

from .models import WaitingRoomEntry
from .services import form_game

User = get_user_model()


def add_waiting_users(count):
    users = []
    for i in range(1, count + 1):
        user = User.objects.create_user(
            username=f"user{i}", email=f"user{i}@example.com", password="Very-secret-123"
        )
        WaitingRoomEntry.objects.create(user=user)
        users.append(user)
    return users


class FormGameTests(TestCase):
    def test_five_waiting_creates_game_and_two_remain(self):
        users = add_waiting_users(5)

        game = form_game()

        self.assertIsNotNone(game)
        self.assertEqual(Game.objects.count(), 1)

        game.refresh_from_db()
        self.assertEqual(game.status, Game.WAITING)
        self.assertIsNone(game.started_at)
        self.assertEqual(game.created_by, users[0])
        self.assertFalse(Round.objects.exists())

        players = GamePlayer.objects.filter(game=game).order_by("player_order")
        self.assertEqual([p.user for p in players], users[:3])
        self.assertEqual([p.player_order for p in players], [1, 2, 3])

        remaining = WaitingRoomEntry.objects.values_list("user", flat=True)
        self.assertEqual(list(remaining), [users[3].id, users[4].id])

    def test_two_waiting_changes_nothing(self):
        users = add_waiting_users(2)

        game = form_game()

        self.assertIsNone(game)
        self.assertEqual(Game.objects.count(), 0)
        self.assertEqual(GamePlayer.objects.count(), 0)

        remaining = WaitingRoomEntry.objects.values_list("user", flat=True)
        self.assertEqual(list(remaining), [users[0].id, users[1].id])
