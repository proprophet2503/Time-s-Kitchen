"""
Sprite and Item classes for Time's Kitchen game
"""

import pygame
import os
from settings import *


class SpriteSheet:
    """Utility class to load and manage game sprites"""
    
    _cache = {}
    
    @classmethod
    def load_image(cls, filename, size=None):
        """Load an image from assets folder with optional resizing"""
        if filename in cls._cache:
            img = cls._cache[filename]
        else:
            path = os.path.join(ASSETS_PATH, filename)
            try:
                img = pygame.image.load(path).convert_alpha()
                cls._cache[filename] = img
            except pygame.error as e:
                print(f"Cannot load image: {path}")
                # Create placeholder
                img = pygame.Surface((64, 64))
                img.fill(RED)
                
        if size:
            img = pygame.transform.scale(img, size)
        return img


class Item(pygame.sprite.Sprite):
    """Represents an item/ingredient in the game"""
    
    ITEM_IMAGES = {
        ItemType.BREAD: "bread.png",
        ItemType.MEAT: "meat.png",
        ItemType.SAUSAGE: "sausage.png",
        ItemType.PASTA: "pasta.png",
        ItemType.COOKED_MEAT: "cooked_meat.png",
        ItemType.COOKED_SAUSAGE: "cooked_sausage.png",
        ItemType.BOILED_PASTA: "boiled_pasta.png",
        ItemType.BURGER: "burger.png",
        ItemType.HOTDOG: "hot dog.png",
        ItemType.PASTA_DISH: "boiled_pasta.png"  # Use boiled pasta for dish
    }
    
    def __init__(self, item_type, x=0, y=0):
        super().__init__()
        self.item_type = item_type
        self.image = self._load_image()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def _load_image(self):
        """Load the appropriate image for this item type"""
        filename = self.ITEM_IMAGES.get(self.item_type, "bread.png")
        return SpriteSheet.load_image(filename, (ITEM_SIZE, ITEM_SIZE))
    
    def get_display_name(self):
        """Get human-readable name for the item"""
        names = {
            ItemType.BREAD: "Bread",
            ItemType.MEAT: "Raw Meat",
            ItemType.SAUSAGE: "Raw Sausage",
            ItemType.PASTA: "Raw Pasta",
            ItemType.COOKED_MEAT: "Cooked Meat",
            ItemType.COOKED_SAUSAGE: "Cooked Sausage",
            ItemType.BOILED_PASTA: "Boiled Pasta",
            ItemType.BURGER: "Burger",
            ItemType.HOTDOG: "Hotdog",
            ItemType.PASTA_DISH: "Pasta"
        }
        return names.get(self.item_type, "Unknown")


class Player(pygame.sprite.Sprite):
    """Player character class"""
    
    def __init__(self, player_num=1, x=0, y=0):
        super().__init__()
        self.player_num = player_num
        self.speed = PLAYER_SPEED
        
        # Load appropriate sprite
        if player_num == 1:
            self.image = SpriteSheet.load_image("player.png", (PLAYER_SIZE, PLAYER_SIZE))
        else:
            self.image = SpriteSheet.load_image("player2.png", (PLAYER_SIZE, PLAYER_SIZE))
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Item being held
        self.held_item = None
        self.held_items = []  # For assembly - can hold multiple items
        
        # Movement direction for rendering
        self.direction = "down"
        
        # Collision rect (smaller than sprite for better gameplay)
        self.collision_rect = pygame.Rect(
            self.rect.x + 10,
            self.rect.y + 10,
            self.rect.width - 20,
            self.rect.height - 20
        )
        
    def update(self, keys, obstacles=None):
        """Update player position based on input"""
        dx, dy = 0, 0
        
        if self.player_num == 1:
            # WASD controls
            if keys[pygame.K_w]:
                dy = -self.speed
                self.direction = "up"
            if keys[pygame.K_s]:
                dy = self.speed
                self.direction = "down"
            if keys[pygame.K_a]:
                dx = -self.speed
                self.direction = "left"
            if keys[pygame.K_d]:
                dx = self.speed
                self.direction = "right"
        else:
            # Arrow keys for player 2
            if keys[pygame.K_UP]:
                dy = -self.speed
                self.direction = "up"
            if keys[pygame.K_DOWN]:
                dy = self.speed
                self.direction = "down"
            if keys[pygame.K_LEFT]:
                dx = -self.speed
                self.direction = "left"
            if keys[pygame.K_RIGHT]:
                dx = self.speed
                self.direction = "right"
        
        # Store old position
        old_x, old_y = self.rect.x, self.rect.y
        
        # Move
        self.rect.x += dx
        self.rect.y += dy
        
        # Update collision rect
        self.collision_rect.x = self.rect.x + 10
        self.collision_rect.y = self.rect.y + 10
        
        # Check boundaries - adjusted for smaller screen
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > SCREEN_WIDTH - self.rect.width:
            self.rect.x = SCREEN_WIDTH - self.rect.width
        if self.rect.y < 70:  # Leave space for UI at top
            self.rect.y = 70
        if self.rect.y > SCREEN_HEIGHT - self.rect.height - 10:
            self.rect.y = SCREEN_HEIGHT - self.rect.height - 10
            
        # Check obstacle collisions
        if obstacles:
            self.collision_rect.x = self.rect.x + 10
            self.collision_rect.y = self.rect.y + 10
            for obstacle in obstacles:
                if hasattr(obstacle, 'collision_rect'):
                    if self.collision_rect.colliderect(obstacle.collision_rect):
                        self.rect.x = old_x
                        self.rect.y = old_y
                        break
                elif hasattr(obstacle, 'rect'):
                    if self.collision_rect.colliderect(obstacle.rect):
                        self.rect.x = old_x
                        self.rect.y = old_y
                        break
        
        # Final collision rect update
        self.collision_rect.x = self.rect.x + 10
        self.collision_rect.y = self.rect.y + 10
    
    def pickup_item(self, item):
        """Pick up an item"""
        if len(self.held_items) < 3:  # Max 3 items
            self.held_items.append(item)
            return True
        return False
    
    def drop_item(self):
        """Drop the last held item"""
        if self.held_items:
            return self.held_items.pop()
        return None
    
    def has_item(self, item_type):
        """Check if player has a specific item type"""
        for item in self.held_items:
            if item.item_type == item_type:
                return True
        return False
    
    def remove_item(self, item_type):
        """Remove a specific item type from held items"""
        for i, item in enumerate(self.held_items):
            if item.item_type == item_type:
                return self.held_items.pop(i)
        return None
    
    def get_held_item_names(self):
        """Get list of held item names"""
        return [item.get_display_name() for item in self.held_items]
    
    def draw(self, screen):
        """Draw the player and held items clearly visible"""
        # Draw player sprite
        screen.blit(self.image, self.rect)
        
        # Draw held items above player head - clearly visible
        if self.held_items:
            # Calculate starting position for held items
            total_width = len(self.held_items) * 35
            start_x = self.rect.centerx - total_width // 2
            
            for i, item in enumerate(self.held_items):
                item_x = start_x + i * 35
                item_y = self.rect.top - 40
                
                # Draw item background circle for visibility
                pygame.draw.circle(screen, (255, 255, 255), 
                                 (item_x + ITEM_SIZE//2, item_y + ITEM_SIZE//2), 
                                 ITEM_SIZE//2 + 2)
                pygame.draw.circle(screen, (100, 100, 100), 
                                 (item_x + ITEM_SIZE//2, item_y + ITEM_SIZE//2), 
                                 ITEM_SIZE//2 + 2, 2)
                
                # Draw the item
                item_img = pygame.transform.scale(item.image, (ITEM_SIZE - 8, ITEM_SIZE - 8))
                screen.blit(item_img, (item_x + 4, item_y + 4))
        
        # Draw player number indicator
        font = pygame.font.Font(None, 20)
        p_text = font.render(f"P{self.player_num}", True, (255, 255, 255))
        p_bg = pygame.Surface((p_text.get_width() + 4, p_text.get_height() + 2))
        p_bg.fill((0, 0, 0))
        p_bg.set_alpha(150)
        screen.blit(p_bg, (self.rect.centerx - p_text.get_width()//2 - 2, self.rect.bottom + 2))
        screen.blit(p_text, (self.rect.centerx - p_text.get_width()//2, self.rect.bottom + 3))


class Customer(pygame.sprite.Sprite):
    """Customer that comes to order food with animations"""
    
    def __init__(self, target_x, target_y, order=None, line_position=0):
        super().__init__()
        self.base_image = SpriteSheet.load_image("customer.png", (PLAYER_SIZE, PLAYER_SIZE))
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()
        
        # Start from right side of screen
        self.rect.x = SCREEN_WIDTH + 50
        self.rect.y = target_y
        
        self.target_x = target_x
        self.target_y = target_y
        self.order = order
        self.line_position = line_position
        
        # States: arriving, waiting, receiving_food, leaving_happy, leaving_corner
        self.state = "arriving"
        self.speed = CUSTOMER_SPEED
        
        # Animation properties
        self.bob_timer = 0
        self.bob_offset = 0
        self.wait_animation_speed = 0.08
        
        # Food holding
        self.held_food = None
        self.food_image = None
        
        # Corner exit position (bottom-right corner)
        self.corner_x = SCREEN_WIDTH - 60
        self.corner_y = SCREEN_HEIGHT - 100
        
    def update(self):
        """Update customer position and animations"""
        if self.state == "arriving":
            if self.rect.x > self.target_x:
                self.rect.x -= self.speed
            else:
                self.rect.x = self.target_x
                self.state = "waiting"
                
        elif self.state == "waiting":
            # Bobbing animation while waiting
            self.bob_timer += self.wait_animation_speed
            self.bob_offset = int(3 * abs(pygame.math.Vector2(0, 1).rotate(self.bob_timer * 60).y))
            
        elif self.state == "receiving_food":
            # Brief pause to show receiving food
            self.state = "leaving_corner"
            
        elif self.state == "leaving_corner":
            # Walk to corner before exiting
            dx = self.corner_x - self.rect.x
            dy = self.corner_y - self.rect.y
            dist = max(abs(dx), abs(dy))
            
            if dist > self.speed:
                # Move towards corner
                if abs(dx) > self.speed:
                    self.rect.x += self.speed if dx > 0 else -self.speed
                if abs(dy) > self.speed:
                    self.rect.y += self.speed if dy > 0 else -self.speed
            else:
                self.state = "leaving"
                
        elif self.state == "leaving":
            # Exit to the right
            if self.rect.x < SCREEN_WIDTH + 100:
                self.rect.x += self.speed
            else:
                self.kill()
    
    def serve(self, food_image=None):
        """Customer has been served, start leaving with food"""
        self.held_food = True
        self.food_image = food_image
        self.state = "receiving_food"
    
    def is_waiting(self):
        return self.state == "waiting"
    
    def update_line_position(self, new_position, new_target_x):
        """Update position in the waiting line"""
        self.line_position = new_position
        self.target_x = new_target_x
        if self.state == "waiting" and self.rect.x != new_target_x:
            self.state = "arriving"  # Move to new position
    
    def draw(self, screen):
        """Draw customer with animations and held food"""
        # Apply bobbing offset if waiting
        draw_y = self.rect.y - self.bob_offset if self.state == "waiting" else self.rect.y
        
        # Draw customer
        screen.blit(self.image, (self.rect.x, draw_y))
        
        # Draw held food above head if carrying
        if self.held_food and self.food_image:
            food_x = self.rect.centerx - 15
            food_y = draw_y - 35
            
            # Draw background circle
            pygame.draw.circle(screen, (255, 255, 255), 
                             (food_x + 15, food_y + 15), 18)
            pygame.draw.circle(screen, (100, 200, 100), 
                             (food_x + 15, food_y + 15), 18, 2)
            
            # Draw food
            small_food = pygame.transform.scale(self.food_image, (30, 30))
            screen.blit(small_food, (food_x, food_y))
        
        # Draw waiting indicator (small dots based on wait time)
        if self.state == "waiting" and self.order:
            # Draw order number above customer
            font = pygame.font.Font(None, 18)
            order_text = font.render(f"#{self.order.order_id}", True, (255, 255, 0))
            text_x = self.rect.centerx - order_text.get_width() // 2
            text_y = draw_y - 15
            screen.blit(order_text, (text_x, text_y))


class Cashier(pygame.sprite.Sprite):
    """NPC Cashier at the counter"""
    
    def __init__(self, x, y):
        super().__init__()
        self.image = SpriteSheet.load_image("NPC.png", (PLAYER_SIZE, PLAYER_SIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Speech bubble for announcing orders
        self.current_message = ""
        self.message_timer = 0
        
    def announce_order(self, order_name):
        """Announce a new order"""
        self.current_message = f"Order: {order_name}!"
        self.message_timer = 180  # Show for 3 seconds at 60 FPS
        
    def update(self):
        """Update message timer"""
        if self.message_timer > 0:
            self.message_timer -= 1
            
    def draw(self, screen):
        """Draw cashier and speech bubble"""
        screen.blit(self.image, self.rect)
        
        # Draw speech bubble if there's a message
        if self.message_timer > 0 and self.current_message:
            font = pygame.font.Font(None, 24)
            text = font.render(self.current_message, True, BLACK)
            
            # Bubble background
            bubble_rect = text.get_rect()
            bubble_rect.centerx = self.rect.centerx
            bubble_rect.bottom = self.rect.top - 5
            
            padding = 8
            bg_rect = bubble_rect.inflate(padding * 2, padding * 2)
            
            pygame.draw.rect(screen, WHITE, bg_rect, border_radius=5)
            pygame.draw.rect(screen, BLACK, bg_rect, 2, border_radius=5)
            
            screen.blit(text, bubble_rect)


class DirtSpot(pygame.sprite.Sprite):
    """Food stain that needs to be cleaned"""
    
    def __init__(self, x, y):
        super().__init__()
        self.image = SpriteSheet.load_image("food_stain.png", (48, 48))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def clean(self):
        """Clean this dirt spot"""
        self.kill()
        return REWARD_CLEANING
