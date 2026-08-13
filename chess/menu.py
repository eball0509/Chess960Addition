"""
Author: Sepehr Bayat | Open Source Chess MVP

Menu system for selecting game mode.
"""

import pygame
from typing import Optional, Tuple, List
from chess.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, UI_BACKGROUND, UI_TEXT, WHITE, BLACK
)


class VariantMenu:
    """Menu for selecting the chess variant (Traditional vs Chess960),
    shown before the opponent-type menu (GameMenu)."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        self.variants = [
            ("Traditional Chess", "standard"),
            ("Chess960 (Fischer Random)", "chess960"),
        ]

        self.button_rects: List[Tuple[pygame.Rect, str]] = []

    def draw(self):
        self.screen.fill(UI_BACKGROUND)

        title = self.font_large.render("Chess MVP", True, UI_TEXT)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        subtitle = self.font_small.render("Select Chess Variant", True, UI_TEXT)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(subtitle, subtitle_rect)

        self.button_rects = []
        button_y = 220
        button_height = 60
        button_spacing = 20
        button_width = 400

        for i, (label, variant) in enumerate(self.variants):
            button_x = (WINDOW_WIDTH - button_width) // 2
            button_rect = pygame.Rect(button_x, button_y + i * (button_height + button_spacing),
                                       button_width, button_height)
            self.button_rects.append((button_rect, variant))

            pygame.draw.rect(self.screen, (70, 70, 70), button_rect)
            pygame.draw.rect(self.screen, UI_TEXT, button_rect, 2)

            text = self.font_medium.render(label, True, UI_TEXT)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)

        instructions = [
            "Click a variant to continue",
            "Press ESC to exit",
        ]
        inst_y = button_y + len(self.variants) * (button_height + button_spacing) + 40
        for i, instruction in enumerate(instructions):
            inst_text = self.font_small.render(instruction, True, UI_TEXT)
            inst_rect = inst_text.get_rect(center=(WINDOW_WIDTH // 2, inst_y + i * 30))
            self.screen.blit(inst_text, inst_rect)

        pygame.display.flip()

    def handle_click(self, pos: Tuple[int, int]) -> Optional[str]:
        x, y = pos
        for button_rect, variant in self.button_rects:
            if button_rect.collidepoint(x, y):
                return variant
        return None

    def run(self) -> Optional[str]:
        """
        Run the variant-selection loop.

        Returns:
            'standard' or 'chess960', or None if the window was closed/ESC.
        """
        running = True
        selected_variant = None

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    selected_variant = None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        selected_variant = None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        variant = self.handle_click(event.pos)
                        if variant:
                            selected_variant = variant
                            running = False

            self.draw()
            pygame.time.Clock().tick(60)

        return selected_variant


class GameMenu:
    """Menu for selecting game mode."""
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize the menu.
        
        Args:
            screen: Pygame surface to draw on
        """
        self.screen = screen
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Game mode options
        self.modes = [
            ("User vs User", "user_vs_user"),
            ("User vs AI (White)", "user_vs_ai_white"),
            ("User vs AI (Black)", "user_vs_ai_black"),
            ("AI vs AI", "ai_vs_ai")
        ]
        
        self.selected_mode: Optional[str] = None
        self.button_rects: List[Tuple[pygame.Rect, str]] = []
    
    def draw(self):
        """Draw the menu."""
        self.screen.fill(UI_BACKGROUND)
        
        # Title
        title = self.font_large.render("Chess MVP", True, UI_TEXT)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font_small.render("Select Game Mode", True, UI_TEXT)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Draw buttons
        self.button_rects = []
        button_y = 220
        button_height = 60
        button_spacing = 20
        button_width = 400
        
        for i, (label, mode) in enumerate(self.modes):
            button_x = (WINDOW_WIDTH - button_width) // 2
            button_rect = pygame.Rect(button_x, button_y + i * (button_height + button_spacing), 
                                      button_width, button_height)
            self.button_rects.append((button_rect, mode))
            
            # Button background
            pygame.draw.rect(self.screen, (70, 70, 70), button_rect)
            pygame.draw.rect(self.screen, UI_TEXT, button_rect, 2)
            
            # Button text
            text = self.font_medium.render(label, True, UI_TEXT)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
        
        # Instructions
        instructions = [
            "Click on a game mode to start",
            "Press ESC to exit"
        ]
        inst_y = button_y + len(self.modes) * (button_height + button_spacing) + 40
        for i, instruction in enumerate(instructions):
            inst_text = self.font_small.render(instruction, True, UI_TEXT)
            inst_rect = inst_text.get_rect(center=(WINDOW_WIDTH // 2, inst_y + i * 30))
            self.screen.blit(inst_text, inst_rect)
        
        pygame.display.flip()
    
    def handle_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """
        Handle mouse click on menu.
        
        Args:
            pos: Mouse position (x, y)
            
        Returns:
            Selected game mode or None
        """
        x, y = pos
        for button_rect, mode in self.button_rects:
            if button_rect.collidepoint(x, y):
                return mode
        return None
    
    def run(self) -> Optional[str]:
        """
        Run the menu loop.
        
        Returns:
            Selected game mode or None if closed
        """
        running = True
        selected_mode = None
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    selected_mode = None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        selected_mode = None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mode = self.handle_click(event.pos)
                        if mode:
                            selected_mode = mode
                            running = False
            
            self.draw()
            pygame.time.Clock().tick(60)
        
        return selected_mode