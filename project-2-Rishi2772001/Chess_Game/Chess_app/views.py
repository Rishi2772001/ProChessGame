# Chess_app/views.py

import chess
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from .forms import LoginForm, JoinForm, MoveForm
from .models import Game, Invite, PlayerGame
from journal.models import JournalEntry
from .utils import fen_to_dict, move_piece  # Import functions from utils.py
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.sessions.models import Session       
from django.utils import timezone 

@csrf_exempt
@login_required
def home(request):
    """
    The main game view. Checks if the user has an active game.
    If not, redirects to 'no_game' view. Handles move submissions and resignations.
    """
    storage = messages.get_messages(request)
    storage.used = True
    current_game = Game.objects.filter(
        Q(player1=request.user) | Q(player2=request.user),
        status='in_progress'
    ).order_by('-id').first()
    
    if not current_game:
        return redirect('no_game') 

    form = MoveForm(request.POST or None)
    
    if request.method == 'POST':
        if 'new_game' in request.POST:
            return resign_game(request, current_game)
        if form.is_valid():
            move_input = form.cleaned_data['move']
            move_result = move_piece(request.user, current_game, move_input)
            if move_result['valid']:
                messages.success(request, 'Move successful.')
            else:
                messages.error(request, move_result['message'])
            return redirect('home')
        else:
            messages.error(request, 'Please enter a valid move.')

    board_data = fen_to_dict(current_game.fen)
    return render(request, 'Chess_app/home.html', {
        'game': current_game,
        'rows': board_data,
        'current_turn': current_game.current_turn.username,
        'chess_form': form
    })

# @csrf_exempt
# def load_board_data(game):
#     board = chess.Board(game.fen)
#     return fen_to_dict(board.fen())

@csrf_exempt
def resign_game(request, game):
    """
    Handles resignation. Updates the game status and declares the winner.
    """
    if not game:
        messages.error(request, "No active game to resign from.")
        return redirect('home')

    if game.status != 'in_progress':
        messages.error(request, "Game is not in progress.")
        return redirect('home')

    winner = game.player2 if game.player1 == request.user else game.player1
    game.status = 'finished'
    game.winner = winner
    game.result = '1-0' if winner == game.player1 else '0-1'
    game.save()
    messages.info(request, "You have resigned. Game over.")
    return redirect('no_game')

@csrf_exempt
def join(request):
    """
    Handles user registration.
    """
    if request.method == 'POST':
        join_form = JoinForm(request.POST)
        if join_form.is_valid():
            user = join_form.save(commit=False)
            user.set_password(join_form.cleaned_data['password1'])
            user.save()
            return redirect('home')
        else:
            return render(request, 'Chess_app/join.html', {'join_form': join_form})
    else:
        join_form = JoinForm()
        return render(request, 'Chess_app/join.html', {'join_form': join_form})

@csrf_exempt
def user_login(request):
    """
    Handles user login.
    """
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    return redirect('home')
                else:
                    return HttpResponse("Your account is not active.")
            else:
                return render(request, 'Chess_app/login.html', {
                    "login_form": login_form, 
                    "error": "Invalid login credentials."
                })
        else:
            return render(request, 'Chess_app/login.html', {"login_form": login_form})
    else:
        return render(request, 'Chess_app/login.html', {"login_form": LoginForm()})

@csrf_exempt
def user_logout(request):
    """
    Logs out the user.
    """
    logout(request)
    return redirect('/')

@csrf_exempt
def about(request):
    """
    Renders the 'About' page.
    """
    return render(request, 'Chess_app/about.html')

@csrf_exempt
def rules(request):
    """
    Renders the 'Rules' page.
    """
    return render(request, 'Chess_app/rules.html')

@csrf_exempt
def history(request):
    """
    Renders the 'History' page.
    """
    return render(request, 'Chess_app/history.html')

@csrf_exempt 
@login_required
def no_game(request):
    active_game = Game.objects.filter(
        Q(player1=request.user) | Q(player2=request.user),
        status='in_progress'
    ).first()
    if active_game:
        return redirect('home')

    active_games = Game.objects.filter(status='in_progress')
    busy_player_ids = set(active_games.values_list('player1_id', flat=True)) | set(
        active_games.values_list('player2_id', flat=True)
    )

    online_user_ids = {
        int(s.get_decoded().get("_auth_user_id"))
        for s in Session.objects.filter(expire_date__gt=timezone.now())
        if s.get_decoded().get("_auth_user_id")
    }

    available_players = (
        User.objects
        .filter(id__in=online_user_ids)
        .exclude(id__in=busy_player_ids)
        .exclude(id=request.user.id)
    )

    player_games = PlayerGame.objects.filter(
        player=request.user,
        is_deleted=False,
        game__status='finished'
    ).order_by('-game__id')

    completed_games_with_journal = []
    for pg in player_games:
        game = pg.game
        opponent = game.player2 if game.player1 == request.user else game.player1
        journal_entry = JournalEntry.objects.filter(user=request.user, game=game).first()
        outcome = (
            'Win' if game.winner == request.user else
            'Tie' if game.winner is None else
            'Loss'
        )
        moves_count = len(game.moves.split(',')) if game.moves else 0
        completed_games_with_journal.append({
            'game': game,
            'opponent': opponent,
            'journal_entry': journal_entry,
            'outcome': outcome,
            'moves_count': moves_count,
        })

    context = {
        'available_players': available_players,
        'completed_games_with_journal': completed_games_with_journal,
    }
    return render(request, 'Chess_app/no_game.html', context)


@csrf_exempt
def guest_access(request):
    """
    Renders a page for guest access.
    """
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'Chess_app/guest_access.html')

@csrf_exempt
@login_required
def check_invite(request):
    """
    Checks if the user has any pending invites.
    """
    invite = Invite.objects.filter(invitee=request.user, accepted=False).first()
    if invite:
        return JsonResponse({
            'invite': True,
            'inviter': invite.inviter.username,
            'invite_id': invite.id
        })
    return JsonResponse({'invite': False})

@csrf_exempt
@login_required
def send_invite(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        player_id = data.get('player_id')
        invitee = get_object_or_404(User, id=player_id)
        if invitee == request.user:
            return JsonResponse({'success': False, 'error': "You cannot invite yourself."})
        if Invite.objects.filter(inviter=request.user, invitee=invitee, accepted=False).exists():
            return JsonResponse({'success': False, 'error': "Invite already sent."})
        Invite.objects.create(inviter=request.user, invitee=invitee)
        
        # Get the updated invite count for the invitee
        invite_count = Invite.objects.filter(invitee=invitee, accepted=False).count()
        
        # Send notification to the invitee
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_{invitee.id}',
            {
                'type': 'notify',
                'message': {
                    'type': 'invite',
                    'inviter': request.user.username,
                    'invite_id': invitee.id,
                    'invite_count': invite_count
                }
            }
        )
        
        return JsonResponse({'success': True, 'player_username': invitee.username})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

@csrf_exempt
@login_required
def accept_invite(request, invite_id):
    invite = get_object_or_404(Invite, id=invite_id, invitee=request.user)
    invite.accepted = True
    invite.save()
    new_game = Game.objects.create(
        player1=invite.inviter,
        player2=invite.invitee,
        current_turn=invite.inviter,
        fen=chess.STARTING_BOARD_FEN,
        status='in_progress',
        moves=''
    )

    # Create PlayerGame entries for both players
    PlayerGame.objects.create(player=invite.inviter, game=new_game)
    PlayerGame.objects.create(player=invite.invitee, game=new_game)

    # Get the updated invite count for the user
    invite_count = Invite.objects.filter(invitee=request.user, accepted=False).count()

    # Notify both players that the game has started
    channel_layer = get_channel_layer()
    game_id = new_game.id

    # Notify the inviter
    async_to_sync(channel_layer.group_send)(
        f'user_{invite.inviter.id}',
        {
            'type': 'notify',
            'message': {
                'type': 'game_started',
                'game_id': game_id,
                'opponent': invite.invitee.username,
            }
        }
    )

    # Notify the invitee (current user)
    async_to_sync(channel_layer.group_send)(
        f'user_{invite.invitee.id}',
        {
            'type': 'notify',
            'message': {
                'type': 'game_started',
                'game_id': game_id,
                'opponent': invite.inviter.username,
            }
        }
    )

    # Send invite count update to invitee
    async_to_sync(channel_layer.group_send)(
        f'user_{request.user.id}',
        {
            'type': 'notify',
            'message': {
                'type': 'invite_count_update',
                'invite_count': invite_count
            }
        }
    )

    return redirect('home')


@csrf_exempt
@login_required
def view_invites(request):
    """
    Displays sent and received game invites.
    """
    sent_invites = Invite.objects.filter(inviter=request.user, accepted=False)
    received_invites = Invite.objects.filter(invitee=request.user, accepted=False) 
    context = {
        'sent_invites': sent_invites,
        'received_invites': received_invites,
    }
    return render(request, 'Chess_app/view_invites.html', context)

@csrf_exempt
@login_required
def decline_invite(request, invite_id):
    """
    Declines a received game invite.
    """
    invite = get_object_or_404(Invite, id=invite_id, invitee=request.user)
    invite.delete()

    # Get the updated invite count
    invite_count = Invite.objects.filter(invitee=request.user, accepted=False).count()

    # Send notification to the user to update the invite count
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{request.user.id}',
        {
            'type': 'notify',
            'message': {
                'type': 'invite_count_update',
                'invite_count': invite_count
            }
        }
    )

    return redirect('view_invites')


@csrf_exempt
@login_required
def delete_game(request, game_id):
    """
    Marks the game as deleted for the current user.
    """
    game = get_object_or_404(Game, id=game_id)
    if request.user != game.player1 and request.user != game.player2:
        messages.error(request, "You don't have permission to delete this game.")
        return redirect('no_game') 
    if request.method == 'POST':
        # Get the PlayerGame entry for this user and game
        try:
            player_game = PlayerGame.objects.get(player=request.user, game=game)
            player_game.is_deleted = True
            player_game.save()
        except PlayerGame.DoesNotExist:
            # Handle the case where the PlayerGame entry doesn't exist
            messages.error(request, "Could not find game for deletion.")
            return redirect('no_game')

        # Optionally, delete journal entries associated with this user and game
        JournalEntry.objects.filter(game=game, user=request.user).delete()
        messages.success(request, "Game deleted from your history.")
        return redirect('no_game')
    else:
        return render(request, 'Chess_app/confirm_delete.html', {'game': game})


# Views related to AJAX polling have been removed since we're now using WebSockets
