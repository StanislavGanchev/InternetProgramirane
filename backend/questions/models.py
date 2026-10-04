from django.core.exceptions import ValidationError
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class BaseQuestion(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="%(class)ss",
    )
    text = models.TextField()

    class Meta:
        abstract = True

    def __str__(self):
        return self.text[:80]


class ChoiceQuestion(BaseQuestion):
    REQUIRED_OPTIONS = 4

    @classmethod
    def validate_options(cls, options):
        """Validate a collection of options (objects or dicts with is_correct)."""
        options = list(options)
        errors = []
        if len(options) != cls.REQUIRED_OPTIONS:
            errors.append(
                f"A choice question must have exactly {cls.REQUIRED_OPTIONS} "
                f"answer options (found {len(options)})."
            )
        correct = sum(
            1
            for option in options
            if (option.get("is_correct") if isinstance(option, dict) else option.is_correct)
        )
        if correct != 1:
            errors.append(
                f"A choice question must have exactly one correct answer (found {correct})."
            )
        if errors:
            raise ValidationError(errors)

    def clean(self):
        super().clean()
        # Options can only be checked once the question exists in the database.
        if self.pk:
            self.validate_options(self.options.all())


class NumericQuestion(BaseQuestion):
    correct_answer = models.IntegerField()


class AnswerOption(models.Model):
    question = models.ForeignKey(
        ChoiceQuestion,
        on_delete=models.CASCADE,
        related_name="options",
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.text
