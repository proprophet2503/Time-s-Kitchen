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
        ItemType.LETTUCE: "lettuce.png",
        ItemType.SAUCE: "sauce.png",
        ItemType.COOKED_MEAT: "cooked_meat.png",
        ItemType.COOKED_SAUSAGE: "cooked_sausage.png",
        ItemType.BOILED_PASTA: "boiled_pasta.png",
        ItemType.BURGER: "burger.png",
        ItemType.HOTDOG: "hot dog.png",
        ItemType.PASTA_DISH: "boiled_pasta.png", # Use boiled pasta for dish
        ItemType.SALAD_DISH: "salad.png",
  
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
            ItemType.LETTUCE: "Lettuce",
            ItemType.SAUCE: "Sauce",
            ItemType.COOKED_MEAT: "Cooked Meat",
            ItemType.COOKED_SAUSAGE: "Cooked Sausage",
            ItemType.BOILED_PASTA: "Boiled Pasta",
            ItemType.BURGER: "Burger",
            ItemType.HOTDOG: "Hotdog",
            ItemType.PASTA_DISH: "Pasta",
            ItemType.SALAD_DISH: "Salad"
        }
        return names.get(self.item_type, "Unknown")


class Player(pygame.sprite.Sprite):
    """Player character class"""
    
    def __init__(self, player_num=1, x=0, y=0, speed_boost=0, holding_boost=0):
        super().__init__()
        self.player_num = player_num
        self.speed = PLAYER_SPEED + speed_boost  # Apply speed perk
        self.max_items = 3 + holding_boost  # Apply holding perk (default 3, can be 4)
        
        # Load appropriate sprite
        if player_num == 1:
            self.image = SpriteSheet.load_image("player.png", (PLAYER1_SIZE, PLAYER1_SIZE))
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
        # Player 1 has smaller collision due to larger sprite size
        if player_num == 1:
            collision_offset_x = 45  # Horizontal offset for player 1
            collision_offset_y = 25  # Vertical offset for player 1
        else:
            collision_offset_x = 15  # Standard horizontal offset for player 2
            collision_offset_y = 15  # Standard vertical offset for player 2
            
        self.collision_rect = pygame.Rect(
            self.rect.x + collision_offset_x,
            self.rect.y + collision_offset_y,
            self.rect.width - (collision_offset_x * 2),
            self.rect.height - (collision_offset_y * 2)
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
        
        # Get collision offsets based on player number
        if self.player_num == 1:
            collision_offset_x = 45
            collision_offset_y = 25
        else:
            collision_offset_x = 15
            collision_offset_y = 15
        
        # Update collision rect with proper offsets
        self.collision_rect.x = self.rect.x + collision_offset_x
        self.collision_rect.y = self.rect.y + collision_offset_y
        
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
            self.collision_rect.x = self.rect.x + collision_offset_x
            self.collision_rect.y = self.rect.y + collision_offset_y
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
        self.collision_rect.x = self.rect.x + collision_offset_x
        self.collision_rect.y = self.rect.y + collision_offset_y
    
    def pickup_item(self, item):
        """Pick up an item"""
        if len(self.held_items) < self.max_items:  # Use max_items instead of hardcoded 3
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
    
    def __init__(self, target_x, target_y, order=None, line_position=0, dining_table=None):
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
        self.dining_table = dining_table
        self.ordered_item = order.dish_type if order else None  # Track what dish they ordered
        
        # States: arriving, waiting, receiving_food, leaving_happy, leaving_corner
        self.state = "arriving"
        self.speed = CUSTOMER_SPEED
        
        # Eating timer
        self.eating_timer = 0
        self.eating_duration = 3.0  # Seconds to eat
        
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
        
    def update(self, dt=1/60):
        """Update customer position and animations"""
        if self.state == "arriving":
            # Walk to cashier first
            if self.rect.x > self.target_x:
                self.rect.x -= self.speed
            else:
                self.rect.x = self.target_x
                # After arriving at cashier, go to table
                if self.dining_table:
                    self.state = "going_to_table"
                else:
                    self.state = "waiting"  # Fallback
                
        elif self.state == "going_to_table":
            # Walk to assigned dining table
            if self.dining_table:
                table_x = self.dining_table.rect.x
                table_y = self.dining_table.rect.y - 20  # Sit slightly above table
                
                dx = table_x - self.rect.x
                dy = table_y - self.rect.y
                dist = (dx**2 + dy**2)**0.5
                
                if dist > self.speed:
                    # Move towards table
                    self.rect.x += int(dx / dist * self.speed)
                    self.rect.y += int(dy / dist * self.speed)
                else:
                    self.rect.x = table_x
                    self.rect.y = table_y
                    self.state = "sitting"
            else:
                self.state = "waiting"  # Fallback
                
        elif self.state == "sitting":
            # Bobbing animation while waiting for food
            self.bob_timer += self.wait_animation_speed
            self.bob_offset = int(2 * abs(pygame.math.Vector2(0, 1).rotate(self.bob_timer * 60).y))
            
        elif self.state == "eating":
            # Eating animation - stay at table
            self.eating_timer += dt
            self.bob_timer += self.wait_animation_speed * 1.5
            self.bob_offset = int(4 * abs(pygame.math.Vector2(0, 1).rotate(self.bob_timer * 60).y))
            
            if self.eating_timer >= self.eating_duration:
                self.state = "leaving"
                
        elif self.state == "waiting":
            # Bobbing animation while waiting (legacy state)
            self.bob_timer += self.wait_animation_speed
            self.bob_offset = int(3 * abs(pygame.math.Vector2(0, 1).rotate(self.bob_timer * 60).y))
            
        elif self.state == "receiving_food":
            # Brief pause to show receiving food
            self.state = "eating"
            self.eating_timer = 0
            
        elif self.state == "leaving":
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
                # Reached corner, now exit
                self.rect.x = self.corner_x
                self.rect.y = self.corner_y
                # Start exiting to the right
                self.state = "exiting"
                
        elif self.state == "exiting":
            # Exit to the right
            if self.rect.x < SCREEN_WIDTH + 100:
                self.rect.x += self.speed
            else:
                # Release dining table when leaving
                if self.dining_table:
                    self.dining_table.occupied = False
                    self.dining_table = None
                self.kill()
    
    def serve(self, food_image=None):
        """Customer has been served, start leaving with food"""
        self.held_food = True
        self.food_image = food_image
        self.state = "receiving_food"
    
    def is_waiting(self):
        return self.state in ["sitting", "waiting"]
    
    def can_receive_delivery(self, item_type):
        """Check if customer can receive this item"""
        return self.state == "sitting" and self.ordered_item == item_type
    
    def receive_delivery(self, food_image=None):
        """Customer receives their order at the table"""
        self.held_food = True
        self.food_image = food_image
        self.state = "receiving_food"
        return True
    
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
        
        # Draw order bubble above customer when sitting at table
        if self.state == "sitting" and self.order and self.ordered_item:
            # Draw speech bubble background
            bubble_width = 50
            bubble_height = 50
            bubble_x = self.rect.centerx - bubble_width // 2
            bubble_y = self.rect.top - bubble_height - 10
            
            # Draw white bubble with border
            bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)
            pygame.draw.rect(screen, (255, 255, 255), bubble_rect, border_radius=8)
            pygame.draw.rect(screen, (100, 100, 100), bubble_rect, 2, border_radius=8)
            
            # Draw small triangle pointing down to customer
            triangle_points = [
                (self.rect.centerx - 5, bubble_y + bubble_height),
                (self.rect.centerx + 5, bubble_y + bubble_height),
                (self.rect.centerx, bubble_y + bubble_height + 8)
            ]
            pygame.draw.polygon(screen, (255, 255, 255), triangle_points)
            pygame.draw.lines(screen, (100, 100, 100), False, triangle_points[:2], 2)
            
            # Draw the ordered dish image in the bubble
            if self.order.image:
                dish_img = pygame.transform.scale(self.order.image, (40, 40))
                screen.blit(dish_img, (bubble_x + 5, bubble_y + 5))
        
        # Draw held food above head if carrying (after eating)
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

class LongTable(pygame.sprite.Sprite):
    """Static long table that separates kitchen and customer area"""

    def __init__(self, x, y, width=None):
        super().__init__()

        if "longtable.png" in SpriteSheet._cache:
            del SpriteSheet._cache["longtable.png"]
        
        # Load image dengan custom width jika diberikan
        if width:
            self.image = SpriteSheet.load_image(
                "longtable.png",
                (width, 100)  # Custom width dengan height 100px (diperbesar)
            )
        else:
            self.image = SpriteSheet.load_image(
                "longtable.png",
                None  # Gunakan ukuran asli PNG
            )

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # COLLISION (player tidak bisa tembus)
        self.collision_rect = pygame.Rect(
            self.rect.x,
            self.rect.y,
            self.rect.width,
            self.rect.height
        )

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


class Pedestrian(pygame.sprite.Sprite):
    """NPC walking on the road for ambience"""
    
    def __init__(self, x, y, direction="down"):
        super().__init__()
        self.image = SpriteSheet.load_image("customer.png", (PLAYER_SIZE, PLAYER_SIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.direction = direction  # "up" or "down"
        self.speed = 1.5
        
    def update(self, dt=1/60):
        """Update pedestrian movement"""
        if self.direction == "down":
            self.rect.y += self.speed
            # Reset to top when reaching bottom
            if self.rect.y > SCREEN_HEIGHT:
                self.rect.y = 50
        else:  # up
            self.rect.y -= self.speed
            # Reset to bottom when reaching top
            if self.rect.y < 50:
                self.rect.y = SCREEN_HEIGHT
    
    def draw(self, screen):
        """Draw the pedestrian"""
        screen.blit(self.image, self.rect)


class Tenant(pygame.sprite.Sprite):
    """Static tenant decoration on the roadside"""
    
    def __init__(self, x, y):
        super().__init__()
        self.image = SpriteSheet.load_image("tenant.png", (100, 100))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def draw(self, screen):
        """Draw the tenant"""
        screen.blit(self.image, self.rect)

