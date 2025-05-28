from django.contrib import admin
from Chess_app.models import Game
from .models import Board

admin.site.register(Game)
admin.site.register(Board)