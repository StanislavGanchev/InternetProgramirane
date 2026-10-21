from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services


def game_data(game):
    players = game.players.select_related("user")
    return {
        "id": game.id,
        "status": game.status,
        "players": [
            {"user_id": p.user_id, "username": p.user.username, "player_order": p.player_order}
            for p in players
        ],
    }


class JoinView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            game = services.join(request.user)
        except services.WaitingRoomError as e:
            return Response({"errors": {"detail": [str(e)]}}, status=status.HTTP_409_CONFLICT)

        if game is None:
            return Response({"waiting": True, "game": None}, status=status.HTTP_201_CREATED)
        return Response({"waiting": False, "game": game_data(game)}, status=status.HTTP_201_CREATED)


class LeaveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not services.leave(request.user):
            return Response(
                {"errors": {"detail": ["You are not in the waiting room."]}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
