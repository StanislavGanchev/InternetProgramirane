from django.urls import path

from .views import JoinView, LeaveView

app_name = "waiting_room"

urlpatterns = [
    path("join/", JoinView.as_view(), name="join"),
    path("leave/", LeaveView.as_view(), name="leave"),
]
