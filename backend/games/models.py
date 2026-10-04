from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from questions.models import AnswerOption, ChoiceQuestion, NumericQuestion


class Game(models.Model):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (WAITING, "Waiting"),
        (IN_PROGRESS, "In Progress"),
        (FINISHED, "Finished"),
        (CANCELLED, "Cancelled"),
    ]

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_games",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=WAITING)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=["waiting", "in_progress", "finished", "cancelled"]),
                name="game_status_valid",
            ),
            models.CheckConstraint(
                condition=Q(finished_at__isnull=True)
                | Q(started_at__isnull=True)
                | Q(finished_at__gte=models.F("started_at")),
                name="game_finished_after_started",
            ),
        ]

    def __str__(self):
        return f"Game #{self.pk} ({self.get_status_display()})"

    def clean(self):
        super().clean()
        if self.status == self.IN_PROGRESS and self.started_at is None:
            raise ValidationError({"started_at": "A game in progress must have a start time."})
        if self.status == self.FINISHED and self.finished_at is None:
            raise ValidationError({"finished_at": "A finished game must have a finish time."})


class GamePlayer(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="players")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="game_players",
    )
    player_order = models.PositiveSmallIntegerField()
    score = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["game", "player_order"]
        constraints = [
            models.UniqueConstraint(fields=["game", "user"], name="unique_user_per_game"),
            models.UniqueConstraint(
                fields=["game", "player_order"], name="unique_player_order_per_game"
            ),
        ]

    def __str__(self):
        return f"{self.user} in game #{self.game_id} (#{self.player_order})"


class Round(models.Model):
    PENDING = "pending"
    OPEN = "open"
    CLOSED = "closed"
    EVALUATED = "evaluated"

    ROUND_STATUS_CHOICES = [
        (PENDING, "Pending"),
        (OPEN, "Open"),
        (CLOSED, "Closed"),
        (EVALUATED, "Evaluated"),
    ]

    CHOICE = "choice"
    NUMERIC = "numeric"

    QUESTION_TYPE_CHOICES = [
        (CHOICE, "Choice"),
        (NUMERIC, "Numeric"),
    ]

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="rounds")
    number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=ROUND_STATUS_CHOICES, default=PENDING)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    choice_question = models.ForeignKey(
        ChoiceQuestion,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="rounds",
    )
    numeric_question = models.ForeignKey(
        NumericQuestion,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="rounds",
    )
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["game", "number"]
        constraints = [
            models.UniqueConstraint(fields=["game", "number"], name="unique_round_number_per_game"),
            models.CheckConstraint(
                condition=Q(number__gte=1),
                name="round_number_positive",
            ),
            models.CheckConstraint(
                condition=Q(status__in=["pending", "open", "closed", "evaluated"]),
                name="round_status_valid",
            ),
            # Exactly one question, and it must match question_type.
            models.CheckConstraint(
                condition=(
                    Q(
                        question_type="choice",
                        choice_question__isnull=False,
                        numeric_question__isnull=True,
                    )
                    | Q(
                        question_type="numeric",
                        choice_question__isnull=True,
                        numeric_question__isnull=False,
                    )
                ),
                name="round_has_one_matching_question",
            ),
        ]

    def __str__(self):
        return f"Round {self.number} of game #{self.game_id}"

    @property
    def question(self):
        if self.question_type == self.CHOICE:
            return self.choice_question
        return self.numeric_question

    def clean(self):
        super().clean()
        if self.question_type == self.CHOICE:
            if self.choice_question_id is None:
                raise ValidationError({"choice_question": "A choice round needs a choice question."})
            if self.numeric_question_id is not None:
                raise ValidationError(
                    {"numeric_question": "A choice round cannot have a numeric question."}
                )
        elif self.question_type == self.NUMERIC:
            if self.numeric_question_id is None:
                raise ValidationError(
                    {"numeric_question": "A numeric round needs a numeric question."}
                )
            if self.choice_question_id is not None:
                raise ValidationError(
                    {"choice_question": "A numeric round cannot have a choice question."}
                )


class RoundAnswer(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name="answers")
    player = models.ForeignKey(GamePlayer, on_delete=models.CASCADE, related_name="answers")
    selected_option = models.ForeignKey(
        AnswerOption,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="round_answers",
    )
    numeric_value = models.IntegerField(null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    points_awarded = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["round", "submitted_at", "id"]
        constraints = [
            models.UniqueConstraint(fields=["round", "player"], name="unique_answer_per_player_round"),
            # Either a selected option or a numeric value, never both.
            models.CheckConstraint(
                condition=Q(selected_option__isnull=True) | Q(numeric_value__isnull=True),
                name="answer_has_single_value_type",
            ),
        ]

    def __str__(self):
        return f"Answer by {self.player} in {self.round}"

    def clean(self):
        super().clean()
        if self.selected_option_id is not None and self.numeric_value is not None:
            raise ValidationError("An answer cannot have both a selected option and a numeric value.")

        if not (self.round_id and self.player_id):
            return

        if self.player.game_id != self.round.game_id:
            raise ValidationError({"player": "The player does not take part in this round's game."})

        if self.round.question_type == Round.CHOICE:
            if self.numeric_value is not None:
                raise ValidationError({"numeric_value": "A choice round expects a selected option."})
            if (
                self.selected_option_id is not None
                and self.selected_option.question_id != self.round.choice_question_id
            ):
                raise ValidationError(
                    {"selected_option": "The option does not belong to this round's question."}
                )
        elif self.round.question_type == Round.NUMERIC and self.selected_option_id is not None:
            raise ValidationError({"selected_option": "A numeric round expects a numeric value."})
