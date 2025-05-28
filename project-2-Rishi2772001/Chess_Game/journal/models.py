from django.db import models
from django.contrib.auth.models import User
from Chess_app.models import Game

class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    game_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Journal Entry for {self.user.username} - Game ID: {self.game.id}"
