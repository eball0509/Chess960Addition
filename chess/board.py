"""
Author: Sepehr Bayat | Open Source Chess MVP

Board class for managing the chess board state, moves, and game rules.
"""

import random
from typing import Optional, Tuple, List
from copy import deepcopy
from chess.pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King
from chess.chess960 import generate_chess960_back_rank, STANDARD_BACK_RANK

# Maps piece-type strings (from a back-rank list) to their classes.
PIECE_CLASSES = {
    "rook": Rook,
    "knight": Knight,
    "bishop": Bishop,
    "queen": Queen,
    "king": King,
}

VARIANT_STANDARD = "standard"
VARIANT_CHESS960 = "chess960"


class Board:
    """Chess board managing piece placement and game state."""
    
    def __init__(self, variant: str = VARIANT_STANDARD, rng: Optional[random.Random] = None):
        """
        Initialize a board.

        Args:
            variant: 'standard' (default) or 'chess960'. Determines how the
                back rank is populated; everything else (pawns, move rules,
                turn order) is identical between variants.
            rng: Optional random.Random for deterministic Chess960 setup in
                tests. Ignored for 'standard'.
        """
        self.grid: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        self.current_turn = 'white'
        self.move_history: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []
        self.en_passant_target: Optional[Tuple[int, int]] = None
        self.variant = variant

        if variant == VARIANT_CHESS960:
            self.back_rank: List[str] = generate_chess960_back_rank(rng)
        else:
            self.back_rank = list(STANDARD_BACK_RANK)

        self._initialize_board()
    
    def _initialize_board(self):
        """Set up the initial chess board position from self.back_rank.

        Pawns are always on rows 1/6 regardless of variant. The back rank
        (rooks/knights/bishops/queen/king) is placed from self.back_rank,
        which is either the fixed standard order or a generated Chess960
        arrangement -- black mirrors white on the same columns either way.
        """
        # Place pawns
        for col in range(8):
            self.grid[6][col] = Pawn('white', 6, col)
            self.grid[1][col] = Pawn('black', 1, col)

        # Place back rank for both sides from the same column layout.
        for col, piece_type in enumerate(self.back_rank):
            piece_cls = PIECE_CLASSES[piece_type]
            self.grid[7][col] = piece_cls('white', 7, col)
            self.grid[0][col] = piece_cls('black', 0, col)
    
    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        """Get the piece at the given position."""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.grid[row][col]
        return None
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if the position is valid (within board bounds)."""
        return 0 <= row < 8 and 0 <= col < 8
    
    def make_move(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        """
        Make a move on the board.
        
        Args:
            start: (row, col) of starting position
            end: (row, col) of ending position
            
        Returns:
            True if move was successful, False otherwise
        """
        start_row, start_col = start
        end_row, end_col = end
        
        piece = self.get_piece(start_row, start_col)
        if piece is None or piece.color != self.current_turn:
            return False
        
        # Check if move is valid
        valid_moves = piece.get_valid_moves(self)
        if end not in valid_moves:
            return False
        
        # Handle en passant capture
        captured_piece = self.get_piece(end_row, end_col)
        if (piece.piece_type == 'pawn' and 
            self.en_passant_target == (end_row, end_col) and
            captured_piece is None):
            # Capture the pawn that moved two squares
            direction = -1 if piece.color == 'white' else 1
            captured_pawn = self.get_piece(end_row - direction, end_col)
            if captured_pawn:
                self.grid[end_row - direction][end_col] = None
        
        # Handle castling
        if piece.piece_type == 'king' and abs(end_col - start_col) == 2:
            if end_col > start_col:  # Kingside
                rook = self.get_piece(start_row, 7)
                self.grid[start_row][7] = None
                self.grid[start_row][5] = rook
                if rook:
                    rook.set_position(start_row, 5)
            else:  # Queenside
                rook = self.get_piece(start_row, 0)
                self.grid[start_row][0] = None
                self.grid[start_row][3] = rook
                if rook:
                    rook.set_position(start_row, 3)
        
        # Update en passant target
        self.en_passant_target = None
        if piece.piece_type == 'pawn' and abs(end_row - start_row) == 2:
            direction = -1 if piece.color == 'white' else 1
            self.en_passant_target = (start_row + direction, start_col)
        
        # Move the piece
        self.grid[start_row][start_col] = None
        self.grid[end_row][end_col] = piece
        piece.set_position(end_row, end_col)
        
        # Handle pawn promotion
        if piece.piece_type == 'pawn' and (end_row == 0 or end_row == 7):
            self.grid[end_row][end_col] = Queen(piece.color, end_row, end_col)
        
        # Record move
        self.move_history.append((start, end))
        
        # Switch turn
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        
        return True
    
    def is_move_safe(self, start_row: int, start_col: int, 
                     end_row: int, end_col: int, color: str) -> bool:
        """
        Check if a move would leave the king in check.
        
        Args:
            start_row, start_col: Starting position
            end_row, end_col: Ending position
            color: Color of the piece making the move
            
        Returns:
            True if move is safe (doesn't leave king in check)
        """
        # Create a temporary board to test the move
        temp_board = self.copy()
        piece = temp_board.get_piece(start_row, start_col)
        if piece is None:
            return False
        
        # Make the move on temp board
        temp_board.grid[start_row][start_col] = None
        temp_board.grid[end_row][end_col] = piece
        piece.set_position(end_row, end_col)
        
        # Check if king is in check after move
        return not temp_board.is_in_check(color)
    
    def is_square_attacked(self, row: int, col: int, by_color: str) -> bool:
        """
        Check if a square is attacked by opponent pieces.
        
        Args:
            row, col: Square to check
            by_color: Color of the piece on the square (we check if opponent can attack)
            
        Returns:
            True if square is attacked by opponent
        """
        opponent_color = 'black' if by_color == 'white' else 'white'
        
        # Check all opponent pieces
        for r in range(8):
            for c in range(8):
                piece = self.get_piece(r, c)
                if piece and piece.color == opponent_color:
                    # Get raw moves without check filtering (for attack detection)
                    raw_moves = self._get_raw_moves(piece)
                    if (row, col) in raw_moves:
                        return True
        
        return False
    
    def _get_raw_moves(self, piece: Piece) -> List[Tuple[int, int]]:
        """Get moves without check filtering (for attack detection)."""
        moves = []
        
        if piece.piece_type == 'pawn':
            direction = -1 if piece.color == 'white' else 1
            # Diagonal captures
            for col_offset in [-1, 1]:
                new_col = piece.col + col_offset
                new_row = piece.row + direction
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    moves.append((new_row, new_col))
        
        elif piece.piece_type == 'rook':
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for dr, dc in directions:
                for i in range(1, 8):
                    new_row = piece.row + (dr * i)
                    new_col = piece.col + (dc * i)
                    if not (0 <= new_row < 8 and 0 <= new_col < 8):
                        break
                    moves.append((new_row, new_col))
                    target = self.get_piece(new_row, new_col)
                    if target is not None:
                        break
        
        elif piece.piece_type == 'knight':
            knight_moves = [
                (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                (1, -2), (1, 2), (2, -1), (2, 1)
            ]
            for dr, dc in knight_moves:
                new_row = piece.row + dr
                new_col = piece.col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    moves.append((new_row, new_col))
        
        elif piece.piece_type == 'bishop':
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dr, dc in directions:
                for i in range(1, 8):
                    new_row = piece.row + (dr * i)
                    new_col = piece.col + (dc * i)
                    if not (0 <= new_row < 8 and 0 <= new_col < 8):
                        break
                    moves.append((new_row, new_col))
                    target = self.get_piece(new_row, new_col)
                    if target is not None:
                        break
        
        elif piece.piece_type == 'queen':
            directions = [
                (0, 1), (0, -1), (1, 0), (-1, 0),
                (1, 1), (1, -1), (-1, 1), (-1, -1)
            ]
            for dr, dc in directions:
                for i in range(1, 8):
                    new_row = piece.row + (dr * i)
                    new_col = piece.col + (dc * i)
                    if not (0 <= new_row < 8 and 0 <= new_col < 8):
                        break
                    moves.append((new_row, new_col))
                    target = self.get_piece(new_row, new_col)
                    if target is not None:
                        break
        
        elif piece.piece_type == 'king':
            king_moves = [
                (-1, -1), (-1, 0), (-1, 1),
                (0, -1),           (0, 1),
                (1, -1),  (1, 0),  (1, 1)
            ]
            for dr, dc in king_moves:
                new_row = piece.row + dr
                new_col = piece.col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    moves.append((new_row, new_col))
        
        return moves
    
    def is_in_check(self, color: str) -> bool:
        """
        Check if the king of the given color is in check.
        
        Args:
            color: 'white' or 'black'
            
        Returns:
            True if king is in check
        """
        # Find the king
        king = None
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.piece_type == 'king' and piece.color == color:
                    king = piece
                    break
            if king:
                break
        
        if king is None:
            return False
        
        # Check if any opponent piece can attack the king's square
        return self.is_square_attacked(king.row, king.col, color)
    
    def get_all_moves(self, color: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Get all valid moves for a given color.
        
        Args:
            color: 'white' or 'black'
            
        Returns:
            List of ((start_row, start_col), (end_row, end_col)) tuples
        """
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    valid_moves = piece.get_valid_moves(self)
                    for end_pos in valid_moves:
                        moves.append(((row, col), end_pos))
        return moves
    
    def is_checkmate(self, color: str) -> bool:
        """
        Check if the given color is in checkmate.
        
        Args:
            color: 'white' or 'black'
            
        Returns:
            True if checkmate
        """
        if not self.is_in_check(color):
            return False
        
        # Check if there are any valid moves
        moves = self.get_all_moves(color)
        return len(moves) == 0
    
    def is_stalemate(self, color: str) -> bool:
        """
        Check if the given color is in stalemate.
        
        Args:
            color: 'white' or 'black'
            
        Returns:
            True if stalemate
        """
        if self.is_in_check(color):
            return False
        
        # Check if there are any valid moves
        moves = self.get_all_moves(color)
        return len(moves) == 0
    
    def copy(self):
        """Create a deep copy of the board."""
        new_board = Board.__new__(Board)  # Create instance without calling __init__
        new_board.grid = [[None for _ in range(8)] for _ in range(8)]
        
        # Copy all pieces
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece:
                    new_board.grid[row][col] = piece.copy()
        
        new_board.current_turn = self.current_turn
        new_board.move_history = self.move_history.copy()
        new_board.en_passant_target = self.en_passant_target
        new_board.variant = self.variant
        new_board.back_rank = list(self.back_rank)
        
        return new_board