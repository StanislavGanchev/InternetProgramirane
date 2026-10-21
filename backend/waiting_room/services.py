from django.db import transaction

from games.models import Game, GamePlayer

from .models import WaitingRoomEntry

PLAYERS_PER_GAME = 3


class WaitingRoomError(Exception):
    pass


@transaction.atomic
def form_game():
    # Takes the first 3 users (by join time) and makes a game from them.
    # With less than 3 users nothing happens.
    entries = list(WaitingRoomEntry.objects.select_related("user")[:PLAYERS_PER_GAME])
    if len(entries) < PLAYERS_PER_GAME:
        return None

    game = Game.objects.create(created_by=entries[0].user)
    for order, entry in enumerate(entries, start=1):
        GamePlayer.objects.create(game=game, user=entry.user, player_order=order)
        entry.delete()

    return game


@transaction.atomic
def join(user):
    if WaitingRoomEntry.objects.filter(user=user).exists():
        raise WaitingRoomError("You are already in the waiting room.")

    in_game = GamePlayer.objects.filter(
        user=user, game__status__in=[Game.WAITING, Game.IN_PROGRESS]
    ).exists()
    if in_game:
        raise WaitingRoomError("You are already in a game.")

    WaitingRoomEntry.objects.create(user=user)
    return form_game()


def leave(user):
    deleted, _ = WaitingRoomEntry.objects.filter(user=user).delete()
    return deleted > 0
