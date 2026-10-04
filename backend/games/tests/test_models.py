from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.test import TestCase
from django.utils import timezone

from games.models import Game, GamePlayer, Round, RoundAnswer

from .factories import (
    add_player,
    make_choice_question,
    make_choice_round,
    make_game,
    make_numeric_round,
    make_user,
)


class GameModelTests(TestCase):
    def test_new_game_defaults(self):
        host = make_user("host")
        game = make_game(host)

        self.assertEqual(game.status, Game.WAITING)
        self.assertIsNotNone(game.created_at)
        self.assertIsNone(game.started_at)
        self.assertIsNone(game.finished_at)
        self.assertEqual(game.created_by, host)
        self.assertIn(game, host.created_games.all())

    def test_status_choices(self):
        self.assertEqual(
            [value for value, _ in Game.STATUS_CHOICES],
            ["waiting", "in_progress", "finished", "cancelled"],
        )
        game = make_game()
        game.status = "paused"
        with self.assertRaises(ValidationError):
            game.full_clean()

    def test_game_lifecycle_timestamps(self):
        game = make_game()
        game.status = Game.IN_PROGRESS
        with self.assertRaises(ValidationError):
            game.full_clean()  # in progress without started_at

        game.started_at = timezone.now()
        game.full_clean()
        game.save()

        game.status = Game.FINISHED
        game.finished_at = timezone.now()
        game.full_clean()
        game.save()
        self.assertEqual(Game.objects.get(pk=game.pk).status, Game.FINISHED)

    def test_creator_with_games_cannot_be_deleted(self):
        host = make_user("host")
        make_game(host)
        with self.assertRaises(ProtectedError):
            host.delete()


class GamePlayerModelTests(TestCase):
    def test_players_belong_to_game_in_order(self):
        game = make_game()
        second = add_player(game, make_user("bob"), order=2)
        first = add_player(game, make_user("alice"), order=1)

        self.assertEqual(list(game.players.all()), [first, second])
        self.assertEqual(first.score, 0)
        self.assertTrue(first.is_active)
        self.assertIsNotNone(first.joined_at)

    def test_user_can_join_many_games(self):
        user = make_user("alice")
        add_player(make_game(make_user("h1")), user, 1)
        add_player(make_game(make_user("h2")), user, 1)
        self.assertEqual(user.game_players.count(), 2)

    def test_deleting_game_removes_players_but_keeps_users(self):
        game = make_game()
        user = make_user("alice")
        add_player(game, user, 1)

        game.delete()
        self.assertEqual(GamePlayer.objects.count(), 0)
        user.refresh_from_db()

    def test_user_in_game_cannot_be_deleted(self):
        game = make_game()
        user = make_user("alice")
        add_player(game, user, 1)
        with self.assertRaises(ProtectedError):
            user.delete()


class RoundModelTests(TestCase):
    def setUp(self):
        self.game = make_game()

    def test_rounds_are_ordered_by_number(self):
        third = make_numeric_round(self.game, number=3)
        first = make_choice_round(self.game, number=1)
        second = make_numeric_round(self.game, number=2)

        self.assertEqual(list(self.game.rounds.all()), [first, second, third])
        self.assertEqual(first.status, Round.PENDING)

    def test_round_question_property(self):
        choice_round = make_choice_round(self.game, number=1)
        numeric_round = make_numeric_round(self.game, number=2)
        self.assertEqual(choice_round.question, choice_round.choice_question)
        self.assertEqual(numeric_round.question, numeric_round.numeric_question)

    def test_round_lifecycle(self):
        round_ = make_choice_round(self.game)
        for status in (Round.OPEN, Round.CLOSED, Round.EVALUATED):
            round_.status = status
            round_.full_clean()
            round_.save()
            self.assertEqual(Round.objects.get(pk=round_.pk).status, status)

    def test_round_needs_question_matching_type(self):
        question, _ = make_choice_question()
        round_ = Round(game=self.game, number=1, question_type=Round.NUMERIC, choice_question=question)
        with self.assertRaises(ValidationError):
            round_.full_clean()

    def test_used_question_cannot_be_deleted(self):
        round_ = make_choice_round(self.game)
        with self.assertRaises(ProtectedError):
            round_.choice_question.delete()

    def test_deleting_game_removes_rounds(self):
        make_choice_round(self.game)
        self.game.delete()
        self.assertEqual(Round.objects.count(), 0)


class RoundAnswerModelTests(TestCase):
    def setUp(self):
        self.game = make_game()
        self.player = add_player(self.game, make_user("alice"), 1)
        self.question, self.options = make_choice_question()
        self.choice_round = make_choice_round(self.game, number=1, question=self.question)
        self.numeric_round = make_numeric_round(self.game, number=2)

    def test_choice_answer(self):
        answer = RoundAnswer.objects.create(
            round=self.choice_round,
            player=self.player,
            selected_option=self.options[0],
            is_correct=True,
            points_awarded=100,
            submitted_at=timezone.now(),
        )
        answer.full_clean()
        self.assertIn(answer, self.choice_round.answers.all())
        self.assertIn(answer, self.player.answers.all())

    def test_numeric_answer_defaults(self):
        answer = RoundAnswer.objects.create(
            round=self.numeric_round, player=self.player, numeric_value=1878
        )
        answer.full_clean()
        self.assertIsNone(answer.is_correct)
        self.assertEqual(answer.points_awarded, 0)
        self.assertIsNone(answer.submitted_at)

    def test_player_answers_in_many_rounds(self):
        RoundAnswer.objects.create(
            round=self.choice_round, player=self.player, selected_option=self.options[1]
        )
        RoundAnswer.objects.create(round=self.numeric_round, player=self.player, numeric_value=5)
        self.assertEqual(self.player.answers.count(), 2)

    def test_answer_validation(self):
        other_question, other_options = make_choice_question("Друг въпрос?")
        other_game = make_game(make_user("other-host"))
        outsider = add_player(other_game, make_user("bob"), 1)

        cases = {
            "option from another question": RoundAnswer(
                round=self.choice_round, player=self.player, selected_option=other_options[0]
            ),
            "numeric value in choice round": RoundAnswer(
                round=self.choice_round, player=self.player, numeric_value=3
            ),
            "option in numeric round": RoundAnswer(
                round=self.numeric_round, player=self.player, selected_option=self.options[0]
            ),
            "player from another game": RoundAnswer(
                round=self.choice_round, player=outsider, selected_option=self.options[0]
            ),
        }
        for name, answer in cases.items():
            with self.subTest(case=name):
                with self.assertRaises(ValidationError):
                    answer.full_clean()

    def test_deleting_round_or_player_removes_answers(self):
        RoundAnswer.objects.create(
            round=self.choice_round, player=self.player, selected_option=self.options[0]
        )
        RoundAnswer.objects.create(round=self.numeric_round, player=self.player, numeric_value=1)

        self.choice_round.delete()
        self.assertEqual(RoundAnswer.objects.count(), 1)
        self.player.delete()
        self.assertEqual(RoundAnswer.objects.count(), 0)

    def test_selected_option_is_protected(self):
        RoundAnswer.objects.create(
            round=self.choice_round, player=self.player, selected_option=self.options[0]
        )
        with self.assertRaises(ProtectedError):
            self.options[0].delete()
