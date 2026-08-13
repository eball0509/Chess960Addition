"""
Integration tests for Chess960 mode through the real Board class (not just
the standalone generator -- these confirm the wiring in board.py is correct).
"""

import random

from chess.board import Board


def test_chess960_board_has_32_pieces():
    board = Board(variant="chess960", rng=random.Random(7))
    count = sum(
        1 for row in range(8) for col in range(8) if board.get_piece(row, col) is not None
    )
    assert count == 32


def test_chess960_bishops_on_opposite_colors():
    for seed in range(20):
        board = Board(variant="chess960", rng=random.Random(seed))
        bishop_cols = [
            col for col in range(8) if board.get_piece(7, col).piece_type == "bishop"
        ]
        assert len(bishop_cols) == 2
        assert bishop_cols[0] % 2 != bishop_cols[1] % 2, (
            f"seed {seed}: bishops on same-color squares"
        )


def test_chess960_king_between_rooks():
    for seed in range(20):
        board = Board(variant="chess960", rng=random.Random(seed))
        rook_cols = sorted(
            col for col in range(8) if board.get_piece(7, col).piece_type == "rook"
        )
        king_col = next(
            col for col in range(8) if board.get_piece(7, col).piece_type == "king"
        )
        assert rook_cols[0] < king_col < rook_cols[1], f"seed {seed}: king not between rooks"


def test_chess960_black_mirrors_white_columns():
    """Black's back rank must use the same column layout as white's, just
    on row 0 instead of row 7 -- this is the Chess960 mirroring rule."""
    board = Board(variant="chess960", rng=random.Random(3))
    for col in range(8):
        white_piece = board.get_piece(7, col)
        black_piece = board.get_piece(0, col)
        assert white_piece.piece_type == black_piece.piece_type, (
            f"col {col}: white has {white_piece.piece_type}, black has {black_piece.piece_type}"
        )


def test_chess960_no_piece_swapped_sides():
    """Same regression guard as the standard-mode test, but for Chess960:
    no black piece should end up colored 'white' or vice versa."""
    board = Board(variant="chess960", rng=random.Random(11))
    for col in range(8):
        assert board.get_piece(0, col).color == "black"
        assert board.get_piece(1, col).color == "black"
        assert board.get_piece(6, col).color == "white"
        assert board.get_piece(7, col).color == "white"


def test_chess960_pawns_unchanged_from_standard():
    """Chess960 only randomizes the back rank -- pawns must still be a full
    row on 1/6 regardless of variant."""
    board = Board(variant="chess960", rng=random.Random(5))
    for col in range(8):
        assert board.get_piece(6, col).piece_type == "pawn"
        assert board.get_piece(6, col).color == "white"
        assert board.get_piece(1, col).piece_type == "pawn"
        assert board.get_piece(1, col).color == "black"


def test_chess960_exact_piece_composition():
    board = Board(variant="chess960", rng=random.Random(9))
    back_rank_types = [board.get_piece(7, col).piece_type for col in range(8)]
    assert sorted(back_rank_types) == sorted(
        ["rook", "rook", "knight", "knight", "bishop", "bishop", "queen", "king"]
    )


def test_chess960_is_randomized_not_fixed():
    """Different seeds should (almost always) produce different layouts --
    guards against someone accidentally hardcoding a single arrangement."""
    layouts = set()
    for seed in range(15):
        board = Board(variant="chess960", rng=random.Random(seed))
        layouts.add(tuple(board.get_piece(7, col).piece_type for col in range(8)))
    assert len(layouts) > 1


def test_chess960_board_variant_flag_is_set():
    board = Board(variant="chess960", rng=random.Random(1))
    assert board.variant == "chess960"


def test_standard_mode_still_default_when_variant_unspecified():
    """Backwards compatibility: calling Board() with no args must still
    produce the traditional layout (existing callers shouldn't break)."""
    board = Board()
    assert board.variant == "standard"
    assert board.get_piece(7, 0).piece_type == "rook"
    assert board.get_piece(7, 4).piece_type == "king"