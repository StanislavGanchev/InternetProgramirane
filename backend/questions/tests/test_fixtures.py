from django.test import TestCase

from questions.models import AnswerOption, Category, ChoiceQuestion, NumericQuestion


class QuestionBankFixtureTests(TestCase):
    fixtures = ["questions/question_bank.json"]

    def test_fixture_counts(self):
        self.assertEqual(Category.objects.count(), 6)
        self.assertEqual(ChoiceQuestion.objects.count(), 12)
        self.assertEqual(AnswerOption.objects.count(), 48)
        self.assertEqual(NumericQuestion.objects.count(), 12)

    def test_fixture_data_is_valid(self):
        for question in ChoiceQuestion.objects.all():
            with self.subTest(question=question.pk):
                self.assertEqual(question.options.count(), 4)
                self.assertEqual(question.options.filter(is_correct=True).count(), 1)
                question.full_clean()

        for question in NumericQuestion.objects.all():
            with self.subTest(numeric=question.pk):
                self.assertIsInstance(question.correct_answer, int)
                question.full_clean()
