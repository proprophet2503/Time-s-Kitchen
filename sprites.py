import pygame
import os
from settings import *


class SpriteSheet:
    _cache = {}
    
    @classmethod
    def load_image(cls, filename, size=None):
        if filename in cls._cache:
            img = cls._cache[filename]
        else:
            path = os.path.join(ASSETS_PATH, filename)
            try:
                img = pygame.image.load(path).convert_alpha()
                cls._cache[filename] = img
            except pygame.error as e:
                print(f"Cannot load image: {path}")
                img = pygame.Surface((64, 64))
                img.fill(RED)
                
        if size:
            img = pygame.transform.scale(img, size)
        return img


class Item(pygame.sprite.Sprite):
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
        ItemType.PASTA_DISH: "boiled_pasta.png", 
        ItemType.SALAD_DISH: "salad.png",
        ItemType.MOP: "mop.png",
    }
    
    def __init__(self, item_type, x=0, y=0):
        super().__init__()
        self.item_type = item_type
        self.image = self._load_image()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def _load_image(self):
        filename = self.ITEM_IMAGES.get(self.item_type, "bread.png")
        return SpriteSheet.load_image(filename, (ITEM_SIZE, ITEM_SIZE))
    
    def get_display_name(self):
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
            ItemType.SALAD_DISH: "Salad",
            ItemType.MOP: "Mop"
        }
        return names.get(self.item_type, "Unknown")


class Player(pygame.sprite.Sprite):
    def __init__(self, player_num=1, x=0, y=0, speed_boost=0, holding_boost=0):
        super().__init__()
        self.player_num = player_num
        self.speed = PLAYER_SPEED + speed_boost  
        self.max_items = 3 + holding_boost  
        
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
        self.held_items = []  
        
        # Mop handling
        self.holding_mop = False
        self.mop_object = None  
        
        # Cleaning animation
        self.is_cleaning = False
        self.cleaning_timer = 0
        self.cleaning_duration = 60  
        self.clean_sway_offset = 0
        self.sway_direction = 1
        
        # Movement direction for rendering
        self.direction = "down"
        
        if player_num == 1:
            collision_offset_x = 45  
            collision_offset_y = 25  
        else:
            collision_offset_x = 15  
            collision_offset_y = 15  
            
        self.collision_rect = pygame.Rect(
            self.rect.x + collision_offset_x,
            self.rect.y + collision_offset_y,
            self.rect.width - (collision_offset_x * 2),
            self.rect.height - (collision_offset_y * 2)
        )
        
    def update(self, keys, obstacles=None):
        if self.is_cleaning:
            self.cleaning_timer += 1
            # Sway animation move left and right
            self.clean_sway_offset = int(10 * pygame.math.Vector2(1, 0).rotate(self.cleaning_timer * 10).x)
            
            if self.cleaning_timer >= self.cleaning_duration:
                # Cleaning animation complete
                self.is_cleaning = False
                self.cleaning_timer = 0
                self.clean_sway_offset = 0
            return  # Don't allow movement during cleaning
        
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
        
        # Check boundaries 
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > SCREEN_WIDTH - self.rect.width:
            self.rect.x = SCREEN_WIDTH - self.rect.width
        if self.rect.y < 70:  
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
    
    def start_cleaning(self):
        if self.holding_mop and not self.is_cleaning:
            self.is_cleaning = True
            self.cleaning_timer = 0
            return True
        return False
    
    def pickup_mop(self, mop):
        if not self.holding_mop:
            self.holding_mop = True
            self.mop_object = mop
            return True
        return False
    
    def drop_mop(self):
        if self.holding_mop:
            mop = self.mop_object
            self.holding_mop = False
            self.mop_object = None
            return mop
        return None
    
    def pickup_item(self, item):
        if len(self.held_items) < self.max_items:  
            self.held_items.append(item)
            return True
        return False
    
    def drop_item(self):
        if self.held_items:
            return self.held_items.pop()
        return None
    
    def has_item(self, item_type):
        for item in self.held_items:
            if item.item_type == item_type:
                return True
        return False
    
    def remove_item(self, item_type):
        for i, item in enumerate(self.held_items):
            if item.item_type == item_type:
                return self.held_items.pop(i)
        return None
    
    def get_held_item_names(self):
        return [item.get_display_name() for item in self.held_items]
    
    def draw(self, screen):
        draw_x = self.rect.x + self.clean_sway_offset
        draw_rect = pygame.Rect(draw_x, self.rect.y, self.rect.width, self.rect.height)
        
        # Draw player sprite
        screen.blit(self.image, draw_rect)
        
        # Draw mop if holding it
        if self.holding_mop and self.mop_object:
            # Draw mop next to player
            mop_x = draw_x + self.rect.width - 10
            mop_y = self.rect.y + self.rect.height // 2
            mop_img = SpriteSheet.load_image("mop.png", (30, 50))
            screen.blit(mop_img, (mop_x, mop_y))
            
            if self.is_cleaning:
                font = pygame.font.Font(None, 18)
                clean_text = font.render("Cleaning...", True, (255, 255, 0))
                screen.blit(clean_text, (self.rect.centerx - 30, self.rect.top - 15))
        
        # Draw held items above player head
        if self.held_items:
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
        self.ordered_item = order.dish_type if order else None  
        
        # States: arriving, waiting, receiving_food, leaving_happy, leaving_corner
        self.state = "arriving"
        self.speed = CUSTOMER_SPEED
        
        # Eating timer
        self.eating_timer = 0
        self.eating_duration = 3.0  
        
        # Animation properties
        self.bob_timer = 0
        self.bob_offset = 0
        self.wait_animation_speed = 0.08
        
        # Food holding
        self.held_food = None
        self.food_image = None
        
        # Corner exit position
        self.corner_x = SCREEN_WIDTH - 60
        self.corner_y = SCREEN_HEIGHT - 100
        
    def update(self, dt=1/60):
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
                    self.state = "waiting" 
                
        elif self.state == "going_to_table":
            # Walk to assigned dining table
            if self.dining_table:
                table_x = self.dining_table.rect.x
                table_y = self.dining_table.rect.y - 20  
                
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
                self.state = "waiting"
                
        elif self.state == "sitting":
            # Bobbing animation while waiting for food
            self.bob_timer += self.wait_animation_speed
            self.bob_offset = int(2 * abs(pygame.math.Vector2(0, 1).rotate(self.bob_timer * 60).y))
            
        elif self.state == "eating":
            # stay at table
            self.eating_timer += dt
            self.bob_timer += self.wait_animation_speed * 1.5
            self.bob_offset = int(4 * abs(pygame.math.Vector2(0, 1).rotate(self.bob_timer * 60).y))
            
            if self.eating_timer >= self.eating_duration:
                self.state = "leaving"
                
        elif self.state == "waiting":
            # Bobbing animation while waiting 
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
        self.held_food = True
        self.food_image = food_image
        self.state = "receiving_food"
    
    def is_waiting(self):
        return self.state in ["sitting", "waiting"]
    
    def can_receive_delivery(self, item_type):
        return self.state == "sitting" and self.ordered_item == item_type
    
    def receive_delivery(self, food_image=None):
        self.held_food = True
        self.food_image = food_image
        self.state = "receiving_food"
        return True
    
    def update_line_position(self, new_position, new_target_x):
        self.line_position = new_position
        self.target_x = new_target_x
        if self.state == "waiting" and self.rect.x != new_target_x:
            self.state = "arriving"  
    
    def draw(self, screen):
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
        
        # Draw waiting indicator 
        if self.state == "waiting" and self.order:
            # Draw order number above customer
            font = pygame.font.Font(None, 18)
            order_text = font.render(f"#{self.order.order_id}", True, (255, 255, 0))
            text_x = self.rect.centerx - order_text.get_width() // 2
            text_y = draw_y - 15
            screen.blit(order_text, (text_x, text_y))


class Cashier(pygame.sprite.Sprite):
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
        self.current_message = f"Order: {order_name}!"
        self.message_timer = 180  
        
    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
            
    def draw(self, screen):
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
    def __init__(self, x, y, width=None):
        super().__init__()

        if "longtable.png" in SpriteSheet._cache:
            del SpriteSheet._cache["longtable.png"]
        
        if width:
            self.image = SpriteSheet.load_image(
                "longtable.png",
                (width, 100)  
            )
        else:
            self.image = SpriteSheet.load_image(
                "longtable.png",
                None  
            )

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # COLLISION 
        self.collision_rect = pygame.Rect(
            self.rect.x,
            self.rect.y,
            self.rect.width,
            self.rect.height
        )

class Mop(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = SpriteSheet.load_image("mop.png", (30, 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_held = False
        self.holder = None 
    
    def update(self):
        if self.is_held and self.holder:
            # Move mop position off-screen or with player 
            self.rect.x = self.holder.rect.x + self.holder.rect.width - 10
            self.rect.y = self.holder.rect.y + self.holder.rect.height // 2
    
    def draw(self, screen):
        if not self.is_held:
            screen.blit(self.image, self.rect)

class DirtSpot(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = SpriteSheet.load_image("food_stain.png", (48, 48))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def clean(self):
        self.kill()
        return REWARD_CLEANING


class Pedestrian(pygame.sprite.Sprite):
    def __init__(self, x, y, direction="down"):
        super().__init__()
        self.image = SpriteSheet.load_image("customer.png", (PLAYER_SIZE, PLAYER_SIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.direction = direction  
        self.speed = 1.5
        
    def update(self, dt=1/60):
        if self.direction == "down":
            self.rect.y += self.speed
            # Reset to top when reaching bottom
            if self.rect.y > SCREEN_HEIGHT:
                self.rect.y = 50
        else:  
            self.rect.y -= self.speed
            # Reset to bottom when reaching top
            if self.rect.y < 50:
                self.rect.y = SCREEN_HEIGHT
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Tenant(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = SpriteSheet.load_image("tenant.png", (100, 100))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Storeboard(pygame.sprite.Sprite):
    
    def __init__(self, x, y):
        super().__init__()
        self.image = SpriteSheet.load_image("storeboard.png", (100, 150))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Bush(pygame.sprite.Sprite):
    def __init__(self, x, y, height=415):
        super().__init__()
        self.image = SpriteSheet.load_image("bush.png", (80, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)

