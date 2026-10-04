from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import AnswerOption, Category, ChoiceQuestion, NumericQuestion


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class AnswerOptionInlineFormSet(forms.BaseInlineFormSet):
    """Enforces four options with exactly one correct answer in the admin."""

    def clean(self):
        super().clean()
        if any(self.errors):
            return
        options = [
            form.cleaned_data
            for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get("DELETE", False)
        ]
        try:
            ChoiceQuestion.validate_options(options)
        except ValidationError as exc:
            raise ValidationError(exc.messages)


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    formset = AnswerOptionInlineFormSet
    extra = 4
    max_num = 4
    min_num = 4

    def get_extra(self, request, obj=None, **kwargs):
        return 0 if obj else 4


@admin.register(ChoiceQuestion)
class ChoiceQuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "category")
    list_filter = ("category",)
    search_fields = ("text",)
    inlines = [AnswerOptionInline]


@admin.register(NumericQuestion)
class NumericQuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "category", "correct_answer")
    list_filter = ("category",)
    search_fields = ("text",)
