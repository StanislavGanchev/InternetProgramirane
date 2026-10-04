from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from games.models import Game, Round, RoundAnswer

from .factories import (
    add_player,
    make_choice_question,
    make_choice_round,
    make_game,
    make_numeric_question,
    make_numeric_round,
    make_user,
)


class DatabaseConstraintTests(TestCase):
    """Constraints that the database itself enforces, even without full_clean()."""

    def setUp(self):
        self.game = make_game()
        self.alice = make_user("alice")

    def assertIntegrityError(self, func):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                func()

    def test_user_joins_game_only_once(self):
        add_player(self.game, self.alice, 1)
        self.assertIntegrityError(lambda: add_player(self.game, self.alice, 2))

    def test_player_order_is_unique_per_game(self):
        add_player(self.game, self.alice, 1)
        self.assertIntegrityError(lambda: add_player(self.game, make_user("bob"), 1))

    def test_same_player_order_in_different_games(self):
        add_player(self.game, self.alice, 1)
        add_player(make_game(make_user("host2")), self.alice, 1)

    def test_round_number_is_unique_per_game(self):
        make_choice_round(self.game, number=1)
        self.assertIntegrityError(lambda: make_numeric_round(self.game, number=1))

    def test_round_number_must_be_positive(self):
        self.assertIntegrityError(lambda: make_choice_round(self.game, number=0))

    def test_round_must_have_exactly_one_matching_question(self):
        choice, _ = make_choice_question()
        numeric = make_numeric_question()
        invalid = {
            "no question": dict(question_type=Round.CHOICE),
            "both questions": dict(
                question_type=Round.CHOICE, choice_question=choice, numeric_question=numeric
            ),
            "choice type with numeric question": dict(
                question_type=Round.CHOICE, numeric_question=numeric
            ),
            "numeric type with choice question": dict(
                question_type=Round.NUMERIC, choice_question=choice
            ),
        }
        for number, (name, fields) in enumerate(invalid.items(), start=1):
            with self.subTest(case=name):
                self.assertIntegrityError(
                    lambda: Round.objects.create(game=self.game, number=number, **fields)
                )

    def test_invalid_status_values_are_rejected(self):
        self.assertIntegrityError(
            lambda: Game.objects.create(created_by=self.alice, status="paused")
        )
        question, _ = make_choice_question()
        self.assertIntegrityError(
            lambda: Round.objects.create(
                game=self.game,
                number=1,
                status="skipped",
                question_type=Round.CHOICE,
                choice_question=question,
            )
        )

    def test_game_cannot_finish_before_it_starts(self):
        now = timezone.now()
        self.assertIntegrityError(
            lambda: Game.objects.create(
                created_by=self.alice, started_at=now, finished_at=now - timedelta(minutes=1)
            )
        )

    def test_one_answer_per_player_per_round(self):
        player = add_player(self.game, self.alice, 1)
        round_ = make_numeric_round(self.game)
        RoundAnswer.objects.create(round=round_, player=player, numeric_value=1)
        self.assertIntegrityError(
            lambda: RoundAnswer.objects.create(round=round_, player=player, numeric_value=2)
        )

    def test_answer_cannot_have_both_value_types(self):
        player = add_player(self.game, self.alice, 1)
        question, options = make_choice_question()
        round_ = make_choice_round(self.game, question=question)
        self.assertIntegrityError(
            lambda: RoundAnswer.objects.create(
                round=round_, player=player, selected_option=options[0], numeric_value=5
            )
        )
