from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.test import TestCase

from questions.models import AnswerOption, Category, ChoiceQuestion, NumericQuestion


def make_choice_question(category, correct_flags=(True, False, False, False)):
    question = ChoiceQuestion.objects.create(category=category, text="Въпрос?")
    for index, is_correct in enumerate(correct_flags):
        AnswerOption.objects.create(
            question=question, text=f"Отговор {index + 1}", is_correct=is_correct
        )
    return question


class CategoryTests(TestCase):
    def test_create_category(self):
        category = Category.objects.create(name="География")
        category.full_clean()
        self.assertEqual(str(category), "География")

    def test_category_name_is_unique(self):
        Category.objects.create(name="История")
        with self.assertRaises(ValidationError):
            Category(name="История").full_clean()
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="История")


class ChoiceQuestionTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Наука")

    def test_create_valid_choice_question(self):
        question = make_choice_question(self.category)

        question.full_clean()
        self.assertEqual(question.category, self.category)
        self.assertEqual(question.options.count(), 4)
        self.assertEqual(question.options.filter(is_correct=True).count(), 1)
        self.assertIn(question, self.category.choicequestions.all())

    def test_invalid_choice_questions(self):
        cases = {
            "three options": (True, False, False),
            "five options": (True, False, False, False, False),
            "no correct answer": (False, False, False, False),
            "two correct answers": (True, True, False, False),
        }
        for name, flags in cases.items():
            with self.subTest(case=name):
                question = make_choice_question(self.category, flags)
                with self.assertRaises(ValidationError):
                    question.full_clean()

    def test_deleting_question_deletes_options(self):
        question = make_choice_question(self.category)
        question.delete()
        self.assertEqual(AnswerOption.objects.count(), 0)

    def test_answer_option_defaults_to_incorrect(self):
        question = ChoiceQuestion.objects.create(category=self.category, text="?")
        option = AnswerOption.objects.create(question=question, text="A")
        self.assertFalse(option.is_correct)


class NumericQuestionTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Спорт")

    def test_create_numeric_question(self):
        question = NumericQuestion.objects.create(
            category=self.category, text="Колко играчи има един футболен отбор?", correct_answer=11
        )
        question.full_clean()
        self.assertEqual(question.correct_answer, 11)
        self.assertIn(question, self.category.numericquestions.all())

    def test_correct_answer_is_required(self):
        question = NumericQuestion(category=self.category, text="?")
        with self.assertRaises(ValidationError):
            question.full_clean()


class ProtectedCategoryTests(TestCase):
    def test_category_with_questions_cannot_be_deleted(self):
        category = Category.objects.create(name="Технологии")
        make_choice_question(category)
        with self.assertRaises(ProtectedError):
            category.delete()

        other = Category.objects.create(name="Изкуство")
        NumericQuestion.objects.create(category=other, text="?", correct_answer=1)
        with self.assertRaises(ProtectedError):
            other.delete()
