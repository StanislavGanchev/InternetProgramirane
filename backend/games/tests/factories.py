"""Small helpers that build test data for the games tests."""

from django.contrib.auth import get_user_model

from games.models import Game, GamePlayer, Round
from questions.models import AnswerOption, Category, ChoiceQuestion, NumericQuestion

User = get_user_model()


def make_user(username):
    return User.objects.create_user(
        username=username, email=f"{username}@example.com", password="Very-secret-123"
    )


def make_category(name="Тест"):
    category, _ = Category.objects.get_or_create(name=name)
    return category


def make_choice_question(text="Коя е столицата на България?"):
    question = ChoiceQuestion.objects.create(category=make_category(), text=text)
    options = [
        AnswerOption.objects.create(question=question, text="София", is_correct=True),
        AnswerOption.objects.create(question=question, text="Пловдив"),
        AnswerOption.objects.create(question=question, text="Варна"),
        AnswerOption.objects.create(question=question, text="Бургас"),
    ]
    return question, options


def make_numeric_question(text="В коя година е Освобождението на България?", answer=1878):
    return NumericQuestion.objects.create(
        category=make_category(), text=text, correct_answer=answer
    )


def make_game(creator=None, **kwargs):
    creator = creator or make_user("host")
    return Game.objects.create(created_by=creator, **kwargs)


def add_player(game, user, order):
    return GamePlayer.objects.create(game=game, user=user, player_order=order)


def make_choice_round(game, number=1, question=None):
    question = question or make_choice_question()[0]
    return Round.objects.create(
        game=game, number=number, question_type=Round.CHOICE, choice_question=question
    )


def make_numeric_round(game, number=1, question=None):
    question = question or make_numeric_question()
    return Round.objects.create(
        game=game, number=number, question_type=Round.NUMERIC, numeric_question=question
    )
