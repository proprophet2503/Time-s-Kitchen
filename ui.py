import pygame
from settings import *


class GameUI:
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 22)
        self.font_tiny = pygame.font.Font(None, 18)
        
    def draw_top_bar(self, time_remaining, score, game_hour):
        # Background 
        pygame.draw.rect(self.screen, (30, 30, 30), (0, 0, SCREEN_WIDTH, 70))
        pygame.draw.line(self.screen, (60, 60, 60), (0, 70), (SCREEN_WIDTH, 70), 2)
        
        # Left side - Score
        score_label = self.font_small.render("Score:", True, WHITE)
        self.screen.blit(score_label, (15, 8))
        
        score_text = f"{score}"
        score_surface = self.font_large.render(score_text, True, WHITE)
        self.screen.blit(score_surface, (15, 25))
        
        # Left side - Time with progress bar
        time_label = self.font_small.render("Time:", True, WHITE)
        self.screen.blit(time_label, (120, 8))
        
        # Time value
        time_val = f"{int(time_remaining)}s"
        time_surface = self.font_medium.render(time_val, True, WHITE)
        self.screen.blit(time_surface, (120, 25))
        
        # Time progress bar
        bar_width = 120
        bar_height = 12
        bar_x = 185
        bar_y = 30
        progress = time_remaining / GAME_DURATION
        
        # Bar background
        pygame.draw.rect(self.screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        # Bar fill - green to yellow to red based on time
        if progress > 0.5:
            bar_color = GREEN
        elif progress > 0.25:
            bar_color = YELLOW
        else:
            bar_color = RED
        pygame.draw.rect(self.screen, bar_color, (bar_x, bar_y, int(bar_width * progress), bar_height))
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
        
        # Right side - Game hour
        hour_text = f"Hour {game_hour}/6"
        hour_surface = self.font_small.render(hour_text, True, LIGHT_GRAY)
        hour_rect = hour_surface.get_rect(right=SCREEN_WIDTH - 15, top=8)
        self.screen.blit(hour_surface, hour_rect)
        
        # Right side - Salary display
        salary_label = self.font_small.render("Salary:", True, WHITE)
        salary_rect = salary_label.get_rect(right=SCREEN_WIDTH - 60, top=35)
        self.screen.blit(salary_label, salary_rect)
        
        salary_text = f"${score}"
        salary_surface = self.font_medium.render(salary_text, True, GREEN)
        salary_val_rect = salary_surface.get_rect(right=SCREEN_WIDTH - 15, top=30)
        self.screen.blit(salary_surface, salary_val_rect)
        
    def draw_player_info(self, players, y_offset=0):
        for i, player in enumerate(players):
            x = 15
            y = SCREEN_HEIGHT - 80 - (i * 85) + y_offset
            
            # Background - dark panel
            info_rect = pygame.Rect(x, y, 200, 75)
            pygame.draw.rect(self.screen, (30, 30, 30), info_rect, border_radius=5)
            pygame.draw.rect(self.screen, (80, 80, 80), info_rect, 2, border_radius=5)
            
            # Player label with color indicator
            player_color = (100, 200, 100) if player.player_num == 1 else (100, 100, 200)
            pygame.draw.rect(self.screen, player_color, (x + 5, y + 5, 6, 25))
            
            player_label = f"Player {player.player_num}"
            label_text = self.font_small.render(player_label, True, WHITE)
            self.screen.blit(label_text, (x + 15, y + 5))
            
            # Controls hint
            if player.player_num == 1:
                controls = "WASD + Space/E/Q"
            else:
                controls = "Arrows + Enter/./,"
            ctrl_text = self.font_tiny.render(controls, True, LIGHT_GRAY)
            self.screen.blit(ctrl_text, (x + 15, y + 22))
            
            # Holding label
            holding_label = self.font_tiny.render("Holding:", True, WHITE)
            self.screen.blit(holding_label, (x + 8, y + 40))
            
            # Held items display
            if player.held_items:
                items_text = ", ".join(player.get_held_item_names()[:2])
                if len(player.held_items) > 2:
                    items_text += f" +{len(player.held_items) - 2}"
                items_color = YELLOW
            else:
                items_text = "None"
                items_color = GRAY
            
            items_surface = self.font_tiny.render(items_text, True, items_color)
            self.screen.blit(items_surface, (x + 60, y + 40))
            
            # Stamina bar (visual placeholder)
            bar_width = 185
            bar_height = 10
            bar_x = x + 8
            bar_y = y + 58
            
            pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(self.screen, GREEN, (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
    
    # draw temporary message
    def draw_message(self, message, duration_alpha=255):
        if message:
            text_surface = self.font_medium.render(message, True, WHITE)
            text_surface.set_alpha(duration_alpha)
            text_rect = text_surface.get_rect(centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT - 120)
            
            # Background
            bg_rect = text_rect.inflate(30, 15)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.fill((40, 40, 40))
            bg_surface.set_alpha(min(220, duration_alpha))
            
            self.screen.blit(bg_surface, bg_rect)
            
            self.screen.blit(bg_surface, bg_rect)
            self.screen.blit(text_surface, text_rect)
    
    def draw_controls_hint(self):
        hints = [
            "SPACE/Enter: Interact",
            "E/Period: Serve",
            "Q/Comma: Drop Item"
        ]
        
        y = SCREEN_HEIGHT - 25
        for i, hint in enumerate(hints):
            text = self.font_tiny.render(hint, True, LIGHT_GRAY)
            x = SCREEN_WIDTH // 2 - 150 + i * 150
            self.screen.blit(text, (x, y))
    
    def draw_order_guide(self, active_orders):
        from orders import ORDER_GUIDES
        
        if not active_orders:
            return
        
        # Get the oldest order (first one to complete)
        first_order = active_orders[0]
        guide = ORDER_GUIDES.get(first_order.dish_type)
        
        if not guide:
            return
        
        # Draw guide panel on the right side 
        panel_width = 280
        panel_height = 100
        panel_x = SCREEN_WIDTH - panel_width - 10
        panel_y = SCREEN_HEIGHT - panel_height - 10
        
        # Background
        bg_surface = pygame.Surface((panel_width, panel_height))
        bg_surface.fill((20, 20, 20))
        bg_surface.set_alpha(220)
        self.screen.blit(bg_surface, (panel_x, panel_y))
        pygame.draw.rect(self.screen, (80, 80, 80), (panel_x, panel_y, panel_width, panel_height), 2, border_radius=5)
        
        # Title
        title_surface = self.font_small.render(guide['name'], True, YELLOW)
        self.screen.blit(title_surface, (panel_x + 10, panel_y + 10))
        
        # Ingredients 
        ingredients_surface = self.font_medium.render(guide['ingredients'], True, WHITE)
        self.screen.blit(ingredients_surface, (panel_x + 10, panel_y + 45))


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 72)
        self.font_menu = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
        self.options = ["Start Game", "How to Play", "High Scores", "Quit"]
        self.selected = 0
        
        # Load background
        try:
            from sprites import SpriteSheet
            self.background = SpriteSheet.load_image("mainmenu.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            self.background = None
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self.options[self.selected]
        return None
    
    def draw(self):
        # Background
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(DARK_BROWN)
        
        # Title
        title = self.font_title.render("TIME'S KITCHEN", True, YELLOW)
        title_rect = title.get_rect(centerx=SCREEN_WIDTH // 2, y=100)
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font_small.render("A Cooking Simulator", True, WHITE)
        subtitle_rect = subtitle.get_rect(centerx=SCREEN_WIDTH // 2, y=170)
        self.screen.blit(subtitle, subtitle_rect)
        
        # Menu options
        for i, option in enumerate(self.options):
            if i == self.selected:
                color = YELLOW
                prefix = ""
            else:
                color = WHITE
                prefix = "  "
            
            text = self.font_menu.render(prefix + option, True, color)
            text_rect = text.get_rect(centerx=SCREEN_WIDTH // 2, y=280 + i * 60)
            self.screen.blit(text, text_rect)
        
        # Instructions
        inst = self.font_small.render("Use Arrow Keys to Navigate, Enter to Select", True, LIGHT_GRAY)
        inst_rect = inst.get_rect(centerx=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT - 50)
        self.screen.blit(inst, inst_rect)


class PlayerSelectMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 56)
        self.font_menu = pygame.font.Font(None, 42)
        self.font_small = pygame.font.Font(None, 28)
        
        self.options = ["1 Player", "2 Players", "Back"]
        self.selected = 0
        
        # Load background
        try:
            from sprites import SpriteSheet
            self.background = SpriteSheet.load_image("selectmenu.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            self.background = None
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self.options[self.selected]
            elif event.key == pygame.K_ESCAPE:
                return "Back"
        return None
    
    def draw(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(DARK_BROWN)
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(150)
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title = self.font_title.render("SELECT PLAYERS", True, YELLOW)
        title_rect = title.get_rect(centerx=SCREEN_WIDTH // 2, y=150)
        self.screen.blit(title, title_rect)
        
        # Options
        for i, option in enumerate(self.options):
            if i == self.selected:
                color = YELLOW
                prefix = ""
            else:
                color = WHITE
                prefix = "  "
            
            text = self.font_menu.render(prefix + option, True, color)
            text_rect = text.get_rect(centerx=SCREEN_WIDTH // 2, y=280 + i * 60)
            self.screen.blit(text, text_rect)
        
        # Player info
        info_1p = "1 Player: WASD to move, SPACE to interact, E to serve, Q to drop"
        info_2p = "2 Players: P1 uses WASD+Space/E/Q, P2 uses Arrows+Enter/./,"
        
        info1 = self.font_small.render(info_1p, True, LIGHT_GRAY)
        info2 = self.font_small.render(info_2p, True, LIGHT_GRAY)
        
        self.screen.blit(info1, (SCREEN_WIDTH // 2 - info1.get_width() // 2, 500))
        self.screen.blit(info2, (SCREEN_WIDTH // 2 - info2.get_width() // 2, 540))


class HowToPlayScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 56)
        self.font_text = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 24)
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                return "Back"
        return None
    
    def draw(self):
        self.screen.fill(DARK_BROWN)
        
        # Title
        title = self.font_title.render("HOW TO PLAY", True, YELLOW)
        title_rect = title.get_rect(centerx=SCREEN_WIDTH // 2, y=30)
        self.screen.blit(title, title_rect)
        
        instructions = [
            "",
            "OBJECTIVE:",
            "Complete as many orders as possible during your 6-hour shift!",
            "Each game hour = 1 real minute. Total shift = 6 minutes.",
            "",
            "CONTROLS (Player 1):",
            "  WASD - Move around the kitchen",
            "  SPACE - Interact with stations (pick up, cook, assemble)",
            "  E - Serve completed dishes",
            "  Q - Drop held item",
            "",
            "CONTROLS (Player 2):",
            "  Arrow Keys - Move around",
            "  ENTER - Interact with stations",
            "  PERIOD (.) - Serve completed dishes",
            "  COMMA (,) - Drop held item",
            "",
            "STATIONS:",
            "  Cooler - Get raw ingredients (Bread, Meat, Sausage, Pasta)",
            "  Stove - Cook Meat and Sausage",
            "  Boiler - Cook Pasta",
            "  Assembly Table - Combine ingredients into dishes",
            "  Serve Counter - Deliver completed orders",
            "  Mop - Clean dirt spots for bonus money ($3)",
            "",
            "RECIPES:",
            "  Burger ($10) = Bread + Cooked Meat",
            "  Hotdog ($8) = Bread + Cooked Sausage",
            "  Pasta ($6) = Boiled Pasta",
            "",
            "Press ENTER or ESC to go back"
        ]
        
        y = 70
        for line in instructions:
            if line.startswith("  "):
                color = LIGHT_GRAY
            elif line.endswith(":"):
                color = ORANGE
            else:
                color = WHITE
            
            text = self.font_small.render(line, True, color)
            self.screen.blit(text, (100, y))
            y += 22


class HighScoreScreen:
    def __init__(self, screen, scores):
        self.screen = screen
        self.scores = scores
        self.font_title = pygame.font.Font(None, 56)
        self.font_score = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                return "Back"
        return None
    
    def draw(self):
        self.screen.fill(DARK_BROWN)
        
        # Title
        title = self.font_title.render("HIGH SCORES", True, YELLOW)
        title_rect = title.get_rect(centerx=SCREEN_WIDTH // 2, y=80)
        self.screen.blit(title, title_rect)
        
        if not self.scores:
            no_scores = self.font_score.render("No high scores yet!", True, WHITE)
            self.screen.blit(no_scores, (SCREEN_WIDTH // 2 - no_scores.get_width() // 2, 250))
        else:
            # Display top 10 scores
            for i, score_entry in enumerate(self.scores[:10]):
                rank = f"{i + 1}."
                score = f"${score_entry['score']}"
                players = f"({score_entry['players']}P)"
                date = score_entry.get('date', '')
                
                rank_text = self.font_score.render(rank, True, ORANGE)
                score_text = self.font_score.render(score, True, GREEN)
                players_text = self.font_small.render(players, True, LIGHT_GRAY)
                date_text = self.font_small.render(date, True, GRAY)
                
                y = 180 + i * 45
                self.screen.blit(rank_text, (SCREEN_WIDTH // 2 - 150, y))
                self.screen.blit(score_text, (SCREEN_WIDTH // 2 - 80, y))
                self.screen.blit(players_text, (SCREEN_WIDTH // 2 + 50, y + 5))
                self.screen.blit(date_text, (SCREEN_WIDTH // 2 + 120, y + 5))
        
        # Back instruction
        back_text = self.font_small.render("Press ENTER or ESC to go back", True, LIGHT_GRAY)
        back_rect = back_text.get_rect(centerx=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT - 50)
        self.screen.blit(back_text, back_rect)


class GameOverScreen:
    def __init__(self, screen, score, num_players, is_high_score=False):
        self.screen = screen
        self.score = score
        self.num_players = num_players
        self.is_high_score = is_high_score
        
        self.font_title = pygame.font.Font(None, 72)
        self.font_score = pygame.font.Font(None, 56)
        self.font_text = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
        
        # Load background image
        try:
            self.background = pygame.image.load("assets/endmenu.png").convert()
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            self.background = None  
        
    def handle_input(self, event):
        """Handle input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return "Menu"
            elif event.key == pygame.K_r:
                return "Restart"
        return None
    
    def draw(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(DARK_BROWN)
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(150)
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title = self.font_title.render("SHIFT COMPLETE!", True, YELLOW)
        title_rect = title.get_rect(centerx=SCREEN_WIDTH // 2, y=120)
        self.screen.blit(title, title_rect)
        
        # Score
        score_label = self.font_text.render("Your Final Salary:", True, WHITE)
        score_rect = score_label.get_rect(centerx=SCREEN_WIDTH // 2, y=220)
        self.screen.blit(score_label, score_rect)
        
        score_text = self.font_score.render(f"${self.score}", True, GREEN)
        score_text_rect = score_text.get_rect(centerx=SCREEN_WIDTH // 2, y=270)
        self.screen.blit(score_text, score_text_rect)
        
        # High score notification
        if self.is_high_score:
            hs_text = self.font_text.render("NEW HIGH SCORE!", True, ORANGE)
            hs_rect = hs_text.get_rect(centerx=SCREEN_WIDTH // 2, y=340)
            self.screen.blit(hs_text, hs_rect)
        
        # Player mode
        mode_text = self.font_small.render(f"Mode: {self.num_players} Player(s)", True, LIGHT_GRAY)
        mode_rect = mode_text.get_rect(centerx=SCREEN_WIDTH // 2, y=400)
        self.screen.blit(mode_text, mode_rect)
        
        # Options
        restart_text = self.font_text.render("Press R to Play Again & Visit Store", True, WHITE)
        restart_rect = restart_text.get_rect(centerx=SCREEN_WIDTH // 2, y=480)
        self.screen.blit(restart_text, restart_rect)
        
        menu_text = self.font_text.render("Press ENTER for Main Menu", True, WHITE)
        menu_rect = menu_text.get_rect(centerx=SCREEN_WIDTH // 2, y=530)
        self.screen.blit(menu_text, menu_rect)
