"""
Time's Kitchen - Main Game Entry Point
A 2D Cooking Simulator Game

Controls:
Player 1: WASD (move), SPACE (interact), E (serve), Q (drop)
Player 2: Arrow Keys (move), ENTER (interact), . (serve), , (drop)
"""

import pygame
import sys
from settings import *
from ui import GameUI, MainMenu, PlayerSelectMenu, HowToPlayScreen, HighScoreScreen, GameOverScreen
from kitchen import Kitchen
from highscore import HighScoreManager


class Game:
    """Main game class managing all game states"""
    
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.state = "menu"  # menu, player_select, how_to_play, high_scores, playing, game_over
        self.num_players = 1
        
        # Components
        self.ui = GameUI(self.screen)
        self.main_menu = MainMenu(self.screen)
        self.player_select = PlayerSelectMenu(self.screen)
        self.how_to_play = HowToPlayScreen(self.screen)
        self.high_score_manager = HighScoreManager()
        self.high_score_screen = HighScoreScreen(self.screen, self.high_score_manager.get_high_scores())
        
        self.kitchen = None
        self.game_over_screen = None
        
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            self._handle_events()
            self._update(dt)
            self._draw()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
    
    def _handle_events(self):
        """Handle all pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            if self.state == "menu":
                result = self.main_menu.handle_input(event)
                if result == "Start Game":
                    self.state = "player_select"
                elif result == "How to Play":
                    self.state = "how_to_play"
                elif result == "High Scores":
                    self.high_score_screen = HighScoreScreen(
                        self.screen, 
                        self.high_score_manager.get_high_scores()
                    )
                    self.state = "high_scores"
                elif result == "Quit":
                    self.running = False
                    
            elif self.state == "player_select":
                result = self.player_select.handle_input(event)
                if result == "1 Player":
                    self.num_players = 1
                    self._start_game()
                elif result == "2 Players":
                    self.num_players = 2
                    self._start_game()
                elif result == "Back":
                    self.state = "menu"
                    
            elif self.state == "how_to_play":
                result = self.how_to_play.handle_input(event)
                if result == "Back":
                    self.state = "menu"
                    
            elif self.state == "high_scores":
                result = self.high_score_screen.handle_input(event)
                if result == "Back":
                    self.state = "menu"
                    
            elif self.state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = "menu"
                        return
                self.kitchen.handle_input(event)
                
            elif self.state == "game_over":
                result = self.game_over_screen.handle_input(event)
                if result == "Menu":
                    self.state = "menu"
                elif result == "Restart":
                    self._start_game()
    
    def _start_game(self):
        """Initialize and start a new game"""
        self.kitchen = Kitchen(self.num_players)
        self.state = "playing"
    
    def _update(self, dt):
        """Update game state"""
        if self.state == "playing":
            self.kitchen.update(dt)
            
            # Check for game over
            if self.kitchen.is_game_over():
                self._end_game()
    
    def _end_game(self):
        """Handle game ending"""
        final_score = self.kitchen.score
        is_high_score = self.high_score_manager.add_score(final_score, self.num_players)
        
        self.game_over_screen = GameOverScreen(
            self.screen,
            final_score,
            self.num_players,
            is_high_score
        )
        self.state = "game_over"
    
    def _draw(self):
        """Render the current game state"""
        if self.state == "menu":
            self.main_menu.draw()
            
        elif self.state == "player_select":
            self.player_select.draw()
            
        elif self.state == "how_to_play":
            self.how_to_play.draw()
            
        elif self.state == "high_scores":
            self.high_score_screen.draw()
            
        elif self.state == "playing":
            self._draw_gameplay()
            
        elif self.state == "game_over":
            self.game_over_screen.draw()
    
    def _draw_gameplay(self):
        """Draw the main gameplay screen"""
        # Clear screen
        self.screen.fill(DARK_BROWN)
        
        # Draw kitchen (including floor)
        self.kitchen.draw(self.screen)
        
        # Draw UI top bar
        stats = self.kitchen.get_stats()
        self.ui.draw_top_bar(
            stats['time_remaining'],
            stats['score'],
            stats['game_hour']
        )
        
        # Draw orders in top bar area
        self.kitchen.draw_orders(self.screen)
        
        # Draw player info at bottom
        self.ui.draw_player_info(list(self.kitchen.players))
        
        # Draw message if any
        message, alpha = self.kitchen.get_message()
        if message:
            self.ui.draw_message(message, alpha)


def main():
    """Entry point"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
