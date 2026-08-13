"""
Baseline tests for the STANDARD chess starting position.

Written before the Chess960 refactor lands, specifically so they can catch
any accidental change to standard setup (piece swapped sides, wrong square,
wrong color) introduced while adding the new mode.
"""

from chess.board import Board

# (row, col) -> expected (piece_type, color) for every piece on a fresh
# standard board. This is the full 32-piece ground truth.
EXPECTED_STANDARD_POSITION = {
    # White back rank (row 7)
    (7, 0): ("rook", "white"), (7, 1): ("knight", "white"),
    (7, 2): ("bishop", "white"), (7, 3): ("queen", "white"),
    (7, 4): ("king", "white"), (7, 5): ("bishop", "white"),
    (7, 6): ("knight", "white"), (7, 7): ("rook", "white"),
    # Black back rank (row 0)
    (0, 0): ("rook", "black"), (0, 1): ("knight", "black"),
    (0, 2): ("bishop", "black"), (0, 3): ("queen", "black"),
    (0, 4): ("king", "black"), (0, 5): ("bishop", "black"),
    (0, 6): ("knight", "black"), (0, 7): ("rook", "black"),
}
# Pawns: row 6 = white, row 1 = black, all 8 columns.
for _col in range(8):
    EXPECTED_STANDARD_POSITION[(6, _col)] = ("pawn", "white")
    EXPECTED_STANDARD_POSITION[(1, _col)] = ("pawn", "black")


def test_standard_starting_position_full_snapshot():
    """Every one of the 32 pieces is the right type, right color, right square."""
    board = Board()
    for (row, col), (expected_type, expected_color) in EXPECTED_STANDARD_POSITION.items():
        piece = board.get_piece(row, col)
        assert piece is not None, f"expected a piece at ({row},{col}), found none"
        assert piece.piece_type == expected_type, (
            f"({row},{col}): expected {expected_type}, got {piece.piece_type}"
        )
        assert piece.color == expected_color, (
            f"({row},{col}): expected {expected_color}, got {piece.color}"
        )


def test_standard_middle_ranks_are_empty():
    """Ranks 2-5 (rows 2-5) should have no pieces on a fresh board."""
    board = Board()
    for row in range(2, 6):
        for col in range(8):
            assert board.get_piece(row, col) is None, f"({row},{col}) should be empty"


def test_standard_piece_count_is_32():
    board = Board()
    count = sum(
        1 for row in range(8) for col in range(8) if board.get_piece(row, col) is not None
    )
    assert count == 32


def test_standard_no_pieces_swapped_sides():
    """Regression guard: no white piece should ever land in rows 0-1 or
    black piece in rows 6-7 on the initial standard board."""
    board = Board()
    for col in range(8):
        assert board.get_piece(0, col).color == "black"
        assert board.get_piece(1, col).color == "black"
        assert board.get_piece(6, col).color == "white"
        assert board.get_piece(7, col).color == "white"


def test_standard_king_starts_on_e_file():
    """Locks in king-on-e-file so a Chess960 refactor can't quietly change
    standard mode's king position (which would also silently break castling)."""
    board = Board()
    assert board.get_piece(7, 4).piece_type == "king"
    assert board.get_piece(0, 4).piece_type == "king"


def test_standard_white_turn_first():
    board = Board()
    assert board.current_turn == "white"