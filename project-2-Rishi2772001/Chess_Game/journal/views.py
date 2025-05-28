
from django.shortcuts import render, redirect, get_object_or_404
from .models import JournalEntry
from Chess_app.models import Game
from .forms import JournalEntryForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages


@login_required
def journal_entries(request):
    completed_games = Game.objects.filter(
        Q(player1=request.user) | Q(player2=request.user),
        status='finished'
    ).order_by('-id')
    game_entries = []
    for game in completed_games:
        opponent = game.player2 if game.player1 == request.user else game.player1
        entry = JournalEntry.objects.filter(user=request.user, game=game).first()
        if game.winner == request.user:
            outcome = 'Win'
        elif game.winner is None:
            outcome = 'Tie'
        else:
            outcome = 'Loss'
        moves_count = len(game.moves.split(',')) if game.moves else 0
        game_entries.append({
            'game': game,
            'opponent': opponent,
            'moves_count': moves_count,
            'outcome': outcome,
            'entry': entry,
        })

    return render(request, 'journal/journal.html', {'game_entries': game_entries})

@login_required
def add_journal_entry(request, game_id):
    game = get_object_or_404(Game, id=game_id, status='finished')
    existing_entry = JournalEntry.objects.filter(user=request.user, game=game).first()
    if existing_entry:
        messages.error(request, 'A journal entry for this game already exists.')
        return redirect('journal_entries')
    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.user = request.user
            new_entry.game = game
            new_entry.save()
            messages.success(request, 'Journal entry added successfully.')
            return redirect('journal_entries')
    else:
        form = JournalEntryForm()
    return render(request, 'journal/add_entry.html', {'form': form, 'game': game})


@login_required
def edit_journal_entry(request, id):
    entry = get_object_or_404(JournalEntry, id=id, user=request.user)
    if request.method == 'POST':
        form = JournalEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('journal_entries')
    else:
        form = JournalEntryForm(instance=entry)
    return render(request, 'journal/edit_entry.html', {'form': form, 'entry': entry})

@login_required
def delete_journal_entry(request, id):
    entry = get_object_or_404(JournalEntry, id=id, user=request.user)
    if request.method == 'POST':
        entry.delete()
        return redirect('journal_entries')
    return render(request, 'journal/confirm_delete.html', {'entry': entry})


def journal_dashboard(request):
    return redirect('journal_entries')