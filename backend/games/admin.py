from django.contrib import admin

from .models import Game, GamePlayer, Round, RoundAnswer


class GamePlayerInline(admin.TabularInline):
    model = GamePlayer
    extra = 0
    readonly_fields = ("joined_at",)
    autocomplete_fields = ("user",)


class RoundInline(admin.TabularInline):
    model = Round
    extra = 0
    show_change_link = True
    fields = ("number", "status", "question_type", "choice_question", "numeric_question")


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "status", "created_at", "started_at", "finished_at")
    list_filter = ("status",)
    search_fields = ("created_by__username", "players__user__username")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("created_by",)
    inlines = [GamePlayerInline, RoundInline]


@admin.register(GamePlayer)
class GamePlayerAdmin(admin.ModelAdmin):
    list_display = ("game", "user", "player_order", "score", "is_active", "joined_at")
    list_filter = ("is_active", "game__status")
    search_fields = ("user__username", "user__profile__nickname")
    readonly_fields = ("joined_at",)


class RoundAnswerInline(admin.TabularInline):
    model = RoundAnswer
    extra = 0


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ("game", "number", "status", "question_type", "started_at", "finished_at")
    list_filter = ("status", "question_type")
    search_fields = ("choice_question__text", "numeric_question__text")
    inlines = [RoundAnswerInline]


@admin.register(RoundAnswer)
class RoundAnswerAdmin(admin.ModelAdmin):
    list_display = (
        "round",
        "player",
        "selected_option",
        "numeric_value",
        "is_correct",
        "points_awarded",
        "submitted_at",
    )
    list_filter = ("is_correct", "round__question_type")
    search_fields = ("player__user__username",)
