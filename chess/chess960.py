"""

Chess960 (Fischer Random Chess) back-rank generation.

Kept in its own module, separate from Board, so the placement logic can be
unit tested in isolation without needing pygame or a full board.

Rules implemented (per https://en.wikipedia.org/wiki/Chess960):
  1. Pawns are on their normal starting squares (unchanged from standard chess).
  2. The two bishops must be on opposite-colored squares.
  3. The king must be strictly between the two rooks (rooks flank the king).
  4. Black's back rank mirrors white's (same arrangement, opposite side of board).

"""

import random
from typing import List, Optional

# Same convention as Piece.piece_type (Piece.__class__.__name__.lower()).
PIECE_SET = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]

STANDARD_BACK_RANK = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]


def generate_chess960_back_rank(rng: Optional[random.Random] = None) -> List[str]:
    """
    Generate one valid, randomized Chess960 back-rank arrangement.

    Args:
        rng: Optional random.Random instance. Pass a seeded instance for
             deterministic/reproducible output in tests; omit for real games.

    Returns:
        List of 8 piece-type strings (index 0 = a-file ... index 7 = h-file)
        satisfying the Chess960 setup constraints.
    """
    rng = rng or random.Random()
    squares: List[Optional[str]] = [None] * 8

    # 1. Bishops on opposite-colored squares: one even index, one odd index.
    light_squares = [i for i in range(8) if i % 2 == 1]
    dark_squares = [i for i in range(8) if i % 2 == 0]
    squares[rng.choice(light_squares)] = "bishop"
    squares[rng.choice(dark_squares)] = "bishop"

    # 2. Queen on any remaining square.
    remaining = [i for i in range(8) if squares[i] is None]
    squares[rng.choice(remaining)] = "queen"

    # 3. Knights on any two remaining squares.
    remaining = [i for i in range(8) if squares[i] is None]
    for sq in rng.sample(remaining, 2):
        squares[sq] = "knight"

    # 4. Remaining 3 squares get Rook / King / Rook, left-to-right, which
    #    guarantees the king ends up strictly between the two rooks.
    remaining = sorted(i for i in range(8) if squares[i] is None)
    assert len(remaining) == 3, f"expected 3 empty squares, got {len(remaining)}"
    squares[remaining[0]] = "rook"
    squares[remaining[1]] = "king"
    squares[remaining[2]] = "rook"

    return squares  # type: ignore[return-value]


def is_valid_chess960_back_rank(back_rank: List[str]) -> bool:
    """
    Validate an arrangement against the Chess960 setup rules. Used by tests
    to check both generated and hand-crafted back ranks.
    """
    if len(back_rank) != 8:
        return False
    if sorted(back_rank) != sorted(PIECE_SET):
        return False

    bishop_cols = [i for i, p in enumerate(back_rank) if p == "bishop"]
    if len(bishop_cols) != 2 or (bishop_cols[0] % 2) == (bishop_cols[1] % 2):
        return False  # bishops on same-colored squares

    rook_cols = [i for i, p in enumerate(back_rank) if p == "rook"]
    if len(rook_cols) != 2:
        return False
    king_col = back_rank.index("king")
    if not (min(rook_cols) < king_col < max(rook_cols)):
        return False  # king not between the rooks

    return True