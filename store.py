"""
Store system for purchasing perks between games
"""

import pygame
from settings import *


class Perk:
    """Represents a purchasable perk"""
    
    def __init__(self, name, description, cost, perk_type):
        self.name = name
        self.description = description
        self.cost = cost
        self.perk_type = perk_type
        self.purchased = False
        
    def can_afford(self, money):
        return money >= self.cost and not self.purchased
        
    def purchase(self):
        self.purchased = True


class Store:
    """Store interface for purchasing perks"""
    
    def __init__(self, money):
        self.money = money
        self.perks = [
            Perk("+1 Speed", "Increase player movement speed by 1", 100, "speed"),
            Perk("+1 Holding", "Hold one more item (max 4)", 120, "holding"),
            Perk("2x Salary", "Double all order rewards", 200, "salary")
        ]
        self.selected_index = 0
        self.active = True
        
        # Message system
        self.message = ""
        self.message_timer = 0
        self.message_color = (255, 255, 255)
        
    def handle_input(self, event):
        """Handle store input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.perks)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.perks)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Try to purchase selected perk
                return self._purchase_perk(self.selected_index)
            elif event.key == pygame.K_r:
                # Ready to play with purchased perks
                self.active = False
                return "replay"
            elif event.key == pygame.K_ESCAPE:
                # Exit to main menu (perks will be lost)
                return "menu"
        return None
    
    def _purchase_perk(self, index):
        """Try to purchase a perk"""
        perk = self.perks[index]
        if perk.purchased:
            self.message = "Already owned!"
            self.message_timer = 120
            self.message_color = (255, 200, 100)
            return "already_owned"
        elif perk.can_afford(self.money):
            perk.purchase()
            self.money -= perk.cost
            self.message = f"Purchased {perk.name}!"
            self.message_timer = 120
            self.message_color = (100, 255, 100)
            return "purchased"
        else:
            self.message = "Not enough money!"
            self.message_timer = 120
            self.message_color = (255, 100, 100)
            return "cannot_afford"
    
    def get_active_perks(self):
        """Get dictionary of active perks"""
        active = {}
        for perk in self.perks:
            if perk.purchased:
                if perk.perk_type == "speed":
                    active["speed_boost"] = 1
                elif perk.perk_type == "holding":
                    active["holding_boost"] = 1
                elif perk.perk_type == "salary":
                    active["salary_multiplier"] = 2
        return active
    
    def draw(self, screen):
        """Draw store interface"""
        WIDTH, HEIGHT = SCREEN_WIDTH, SCREEN_HEIGHT
        
        # Draw semi-transparent background
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Store box
        box_width, box_height = 600, 500
        box_x, box_y = WIDTH//2 - box_width//2, HEIGHT//2 - box_height//2
        
        # Shadow
        shadow = pygame.Surface((box_width + 10, box_height + 10), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 150), shadow.get_rect(), border_radius=20)
        screen.blit(shadow, (box_x - 5, box_y + 5))
        
        # Main box
        box = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(box, (30, 30, 30, 250), (0, 0, box_width, box_height), border_radius=20)
        pygame.draw.rect(box, (255, 215, 0), (0, 0, box_width, box_height), 3, border_radius=20)
        screen.blit(box, (box_x, box_y))
        
        # Title
        title_font = pygame.font.Font(None, 70)
        title = title_font.render("PERKS STORE", True, (255, 215, 0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, box_y + 25))
        
        # Money display
        money_font = pygame.font.Font(None, 40)
        money_text = money_font.render(f"Money: ${self.money}", True, (100, 255, 100))
        screen.blit(money_text, (WIDTH//2 - money_text.get_width()//2, box_y + 90))
        
        # Draw line
        pygame.draw.line(screen, (255, 215, 0), 
                        (box_x + 50, box_y + 130), 
                        (box_x + box_width - 50, box_y + 130), 2)
        
        # Draw perks
        perk_start_y = box_y + 160
        for i, perk in enumerate(self.perks):
            perk_y = perk_start_y + (i * 90)
            
            # Selection highlight
            if i == self.selected_index:
                highlight = pygame.Surface((box_width - 60, 80), pygame.SRCALPHA)
                pygame.draw.rect(highlight, (255, 215, 0, 50), (0, 0, box_width - 60, 80), border_radius=10)
                pygame.draw.rect(highlight, (255, 215, 0, 150), (0, 0, box_width - 60, 80), 2, border_radius=10)
                screen.blit(highlight, (box_x + 30, perk_y - 5))
            
            # Perk name and cost
            name_font = pygame.font.Font(None, 36)
            if perk.purchased:
                name_color = (100, 255, 100)
                name = name_font.render(f"✓ {perk.name} - OWNED", True, name_color)
            else:
                name_color = (255, 255, 255) if perk.can_afford(self.money) else (150, 150, 150)
                name = name_font.render(f"{perk.name} - ${perk.cost}", True, name_color)
            screen.blit(name, (box_x + 50, perk_y + 5))
            
            # Description
            desc_font = pygame.font.Font(None, 28)
            desc_color = (200, 200, 200) if not perk.purchased else (150, 200, 150)
            desc = desc_font.render(perk.description, True, desc_color)
            screen.blit(desc, (box_x + 50, perk_y + 40))
        
        # Instructions
        inst_y = box_y + box_height - 60
        inst_font = pygame.font.Font(None, 30)
        inst1 = inst_font.render("ENTER: Buy  R: Play Again  ESC: Main Menu", True, (200, 200, 200))
        screen.blit(inst1, (WIDTH//2 - inst1.get_width()//2, inst_y))
        
        # Draw message notification
        if self.message_timer > 0:
            msg_font = pygame.font.Font(None, 40)
            msg_surface = msg_font.render(self.message, True, self.message_color)
            
            # Message background
            msg_bg_width = msg_surface.get_width() + 40
            msg_bg_height = msg_surface.get_height() + 20
            msg_bg = pygame.Surface((msg_bg_width, msg_bg_height), pygame.SRCALPHA)
            pygame.draw.rect(msg_bg, (0, 0, 0, 200), (0, 0, msg_bg_width, msg_bg_height), border_radius=10)
            
            # Position at top center
            msg_x = WIDTH//2 - msg_bg_width//2
            msg_y = 50
            
            screen.blit(msg_bg, (msg_x, msg_y))
            screen.blit(msg_surface, (msg_x + 20, msg_y + 10))
            
            # Decrease timer
            self.message_timer -= 1


class GameSession:
    """Manages money and perks across game replays"""
    
    def __init__(self):
        self.total_money = 0
        self.active_perks = {}
        self.store = None
        
    def end_game(self, final_score):
        """Called when game ends"""
        self.total_money = final_score
        self.store = Store(self.total_money)
        
    def get_perks(self):
        """Get active perks for current session"""
        return self.active_perks
    
    def apply_store_perks(self):
        """Apply perks from store after purchase"""
        if self.store:
            self.active_perks = self.store.get_active_perks()
            self.total_money = self.store.money
    
    def reset_session(self):
        """Reset session (called when returning to main menu)"""
        self.total_money = 0
        self.active_perks = {}
        self.store = None
