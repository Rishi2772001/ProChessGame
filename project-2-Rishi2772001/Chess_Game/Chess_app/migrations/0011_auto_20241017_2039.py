# Chess_app/migrations/000X_set_current_turn.py
from django.db import migrations

def set_current_turn(apps, schema_editor):
    Game = apps.get_model('Chess_app', 'Game')
    for game in Game.objects.filter(current_turn__isnull=True):
        # Determine who should have the next turn
        # Example logic: If moves are even, it's player1's turn; otherwise, player2's
        if game.moves:
            move_count = len(game.moves.split(','))
        else:
            move_count = 0
        if move_count % 2 == 0:
            game.current_turn = game.player1
        else:
            game.current_turn = game.player2
        game.save()

class Migration(migrations.Migration):

    dependencies = [
        ('Chess_app', '0010_alter_game_current_turn_alter_game_fen_and_more'),
    ]

    operations = [
        migrations.RunPython(set_current_turn),
    ]
