# Chess_app/utils.py

import chess
from .models import Game
from django.contrib.auth.models import User

def fen_to_dict(fen_string):
    piece_to_html = {
        'K': '&#9812;', 'Q': '&#9813;', 'R': '&#9814;', 'B': '&#9815;', 'N': '&#9816;', 'P': '&#9817;',
        'k': '&#9818;', 'q': '&#9819;', 'r': '&#9820;', 'b': '&#9821;', 'n': '&#9822;', 'p': '&#9823;',
    }
    position_part = fen_string.split(' ')[0]
    ranks = position_part.split('/')
    rows_list = []
    for rank_index, rank_str in enumerate(ranks):
        rank_number = 8 - rank_index
        rank_dict = {}
        file_index = 0
        for c in rank_str:
            if c.isdigit():
                for _ in range(int(c)):
                    file_letter = chr(ord('a') + file_index)
                    position = f"{file_letter}{rank_number}"
                    rank_dict[position] = '&nbsp;'
                    file_index += 1
            else:
                file_letter = chr(ord('a') + file_index)
                position = f"{file_letter}{rank_number}"
                rank_dict[position] = piece_to_html.get(c, '&nbsp;')
                file_index += 1
        rows_list.append(rank_dict)
    return rows_list

def move_piece(user, game, move_input):
    if not game:
        return {'valid': False, 'message': 'No active game.'}
    if user != game.current_turn:
        return {'valid': False, 'message': "It's not your turn."}
    board = chess.Board(game.fen)
    try:
        move = chess.Move.from_uci(move_input.strip().lower())
    except ValueError:
        return {'valid': False, 'message': 'Invalid move format. Please enter moves like e2e4.'}
    if move in board.legal_moves:
        board.push(move)
        game.fen = board.fen()
        game.moves = f"{game.moves},{move.uci()}" if game.moves else move.uci()
        game.current_turn = game.player1 if game.current_turn == game.player2 else game.player2

        if board.is_game_over():
            game.status = 'finished'
            if board.is_checkmate():
                winner = user
                game.winner = winner
                game.result = '1-0' if winner == game.player1 else '0-1'
            else:
                game.winner = None
                game.result = '1/2-1/2'

        game.save()
        board_data = fen_to_dict(game.fen)
        return {
            'valid': True,
            'message': 'Move made successfully',
            'fen': game.fen,
            'board': board_data,
            'current_turn': game.current_turn.username,
            'status': game.status,
            'winner': game.winner.username if game.winner else None,
            'result': game.result
        }
    else:
        return {'valid': False, 'message': 'Illegal move'}
