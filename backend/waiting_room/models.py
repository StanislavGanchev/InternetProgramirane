from django.conf import settings
from django.db import models


class WaitingRoomEntry(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="waiting_entry",
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["joined_at", "id"]

    def __str__(self):
        return f"{self.user} (waiting)"
