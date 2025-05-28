from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils import timezone

class Game(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('finished', 'Finished'),
    ]
    player1 = models.ForeignKey(User, related_name='games_as_player1', on_delete=models.CASCADE)
    player2 = models.ForeignKey(User, related_name='games_as_player2', on_delete=models.CASCADE)
    current_turn = models.ForeignKey(User, related_name='current_turn', on_delete=models.CASCADE)
    fen = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    winner = models.ForeignKey(User, related_name='won_games', on_delete=models.SET_NULL, null=True, blank=True)
    moves = models.TextField(null=True, blank=True)
    result = models.CharField(max_length=10, null=True, blank=True)

    def get_opponent(self, user):
        """Return the opponent of the given user in this game."""
        return self.player2 if self.player1 == user else self.player1

    def __str__(self):
        return f"Game between {self.player1} and {self.player2}"

class Board(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.CharField(max_length=255, default='')  # Stores the board state in simple notation
    location = models.CharField(max_length=4)

    class Meta:
        unique_together = (('user', 'location'),)

    def __str__(self):
        return f"{self.user.username}'s board at {self.location}"

class Invite(models.Model):
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invites')
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invites')
    accepted = models.BooleanField(default=False)
    def __str__(self):
        return f"Invite from {self.inviter} to {self.invitee}"
    
class PlayerGame(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('player', 'game')