"""
Order system for Time's Kitchen game
"""

import pygame
import random
import time
from settings import *


class Order:
    """Represents a customer order"""
    
    def __init__(self, dish_type, order_id):
        self.dish_type = dish_type
        self.order_id = order_id
        self.completed = False
        self.timestamp = time.time()
        self.completion_time = None
        
        recipe = RECIPES.get(dish_type, {})
        self.reward = recipe.get("reward", 0)
        self.name = recipe.get("name", "Unknown")
        
        self.image = self._load_image()
        self.wait_time = 0
        
        # Link to customer and dining table
        self.customer = None
        self.dining_table = None
        
    def _load_image(self):
        from sprites import SpriteSheet
        image_files = {
            ItemType.BURGER: "burger.png",
            ItemType.HOTDOG: "hot dog.png",
            ItemType.PASTA_DISH: "boiled_pasta.png",
            ItemType.SALAD_DISH: "salad.png"
        }
        filename = image_files.get(self.dish_type, "burger.png")
        return SpriteSheet.load_image(filename, (40, 40))
    
    def update(self, dt):
        if not self.completed:
            self.wait_time += dt
                
    def complete(self):
        self.completed = True
        self.completion_time = time.time()
        return self.reward
    
    def get_wait_time_str(self):
        minutes = int(self.wait_time // 60)
        seconds = int(self.wait_time % 60)
        return f"{minutes}:{seconds:02d}"


class CompletedOrder:
    """Tracks a completed order for display"""
    
    def __init__(self, order_name, reward, dish_image):
        self.order_name = order_name
        self.reward = reward
        self.dish_image = dish_image
        self.display_timer = 3.0
        
    def update(self, dt):
        self.display_timer -= dt
        return self.display_timer > 0


class OrderManager:
    """Manages all orders in the game"""
    
    def __init__(self, num_players=1):
        self.orders = []
        self.completed_orders = []
        self.all_completed = []
        self.num_players = num_players
        self.orders_per_hour = ORDERS_PER_HOUR_SINGLE if num_players == 1 else ORDERS_PER_HOUR_MULTI
        
        self.spawn_interval = GAME_HOUR / self.orders_per_hour
        self.spawn_timer = 0
        self.total_spawned = 0
        self.order_counter = 0
        
        self.total_reward = 0
        self.total_completed = 0
        
        self.dish_types = [ItemType.BURGER, ItemType.HOTDOG, ItemType.PASTA_DISH, ItemType.SALAD_DISH]
        
        self.on_new_order = None
        self.on_order_complete = None
        
    def update(self, dt, game_time_remaining):
        for order in self.orders:
            order.update(dt)
        
        self.completed_orders = [co for co in self.completed_orders if co.update(dt)]
        
        if game_time_remaining > 10:
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_interval:
                self.spawn_timer = 0
                self._spawn_order()
    
    def _spawn_order(self):
        max_active = 8 if self.num_players == 1 else 12
        active_orders = [o for o in self.orders if not o.completed]
        
        if len(active_orders) < max_active:
            self.order_counter += 1
            dish_type = random.choice(self.dish_types)
            new_order = Order(dish_type, self.order_counter)
            self.orders.append(new_order)
            self.total_spawned += 1
            
            if self.on_new_order:
                self.on_new_order(new_order)
    
    def try_fulfill_order(self, dish_type):
        for order in self.orders:
            if order.dish_type == dish_type and not order.completed:
                reward = order.complete()
                self.total_reward += reward
                self.total_completed += 1
                
                completed = CompletedOrder(order.name, reward, order.image)
                self.completed_orders.append(completed)
                self.all_completed.append(order)
                
                self.orders.remove(order)
                
                if self.on_order_complete:
                    self.on_order_complete(order)
                
                return True, reward, order
        
        return False, 0, None
    
    def get_active_orders(self):
        return [o for o in self.orders if not o.completed]
    
    def draw(self, screen, x, y, max_display=4):
        font = pygame.font.Font(None, 18)
        small_font = pygame.font.Font(None, 16)
        
        active_orders = self.get_active_orders()
        active_orders.sort(key=lambda o: o.wait_time, reverse=True)
        
        order_width = 120  # Increased from 95 to 120
        order_height = 55  # Increased from 48 to 55
        start_x = 320
        
        for i, order in enumerate(active_orders[:max_display]):
            order_x = start_x + i * (order_width + 5)
            order_y = 8
            
            if order.wait_time > 60:
                bg_color = (150, 60, 60)
            elif order.wait_time > 30:
                bg_color = (150, 120, 60)
            else:
                bg_color = (60, 100, 60)
            
            order_rect = pygame.Rect(order_x, order_y, order_width, order_height)
            pygame.draw.rect(screen, bg_color, order_rect, border_radius=5)
            pygame.draw.rect(screen, WHITE, order_rect, 2, border_radius=5)
            
            num_text = small_font.render(f"#{order.order_id}", True, LIGHT_GRAY)
            screen.blit(num_text, (order_x + 5, order_y + 3))
            
            name_text = font.render(order.name.upper(), True, WHITE)
            name_rect = name_text.get_rect(centerx=order_x + order_width//2, top=order_y + 3)
            screen.blit(name_text, name_rect)
            
            wait_text = small_font.render(order.get_wait_time_str(), True, YELLOW)
            wait_rect = wait_text.get_rect(right=order_x + order_width - 5, top=order_y + 3)
            screen.blit(wait_text, wait_rect)
            
            img_x = order_x + order_width//2 - 15
            img_y = order_y + 18
            small_img = pygame.transform.scale(order.image, (30, 30))
            screen.blit(small_img, (img_x, img_y))
        
        if len(active_orders) > max_display:
            more_x = start_x + max_display * (order_width + 5)
            more_text = font.render(f"+{len(active_orders) - max_display} more", True, YELLOW)
            screen.blit(more_text, (more_x, 25))
        
        self._draw_completed_orders(screen)
        self._draw_stats(screen)
    
    def _draw_completed_orders(self, screen):
        if not self.completed_orders:
            return
        
        font = pygame.font.Font(None, 28)
        small_font = pygame.font.Font(None, 22)
        
        y = 75
        for co in self.completed_orders:
            alpha = min(255, int(co.display_timer * 85))
            
            bg_width = 200
            bg_height = 40
            bg_x = SCREEN_WIDTH // 2 - bg_width // 2
            
            bg_surface = pygame.Surface((bg_width, bg_height))
            bg_surface.fill((40, 120, 40))
            bg_surface.set_alpha(alpha)
            screen.blit(bg_surface, (bg_x, y))
            
            pygame.draw.rect(screen, GREEN, (bg_x, y, bg_width, bg_height), 2, border_radius=5)
            
            text = font.render(f"Done: {co.order_name}", True, WHITE)
            screen.blit(text, (bg_x + 10, y + 5))
            
            reward_text = small_font.render(f"+${co.reward}", True, YELLOW)
            screen.blit(reward_text, (bg_x + bg_width - 50, y + 10))
            
            y += 45
    
    def _draw_stats(self, screen):
        font = pygame.font.Font(None, 20)
        stats_text = f"Completed: {self.total_completed} | Total: ${self.total_reward}"
        text_surface = font.render(stats_text, True, LIGHT_GRAY)
        text_rect = text_surface.get_rect(right=SCREEN_WIDTH - 10, top=58)
        screen.blit(text_surface, text_rect)


ORDER_GUIDES = {
    ItemType.BURGER: {
        "name": "How To Make Burger",
        "ingredients": "Bread + Meat"
    },
    ItemType.HOTDOG: {
        "name": "How To Make Hotdog",
        "ingredients": "Bread + Sausage"
    },
    ItemType.PASTA_DISH: {
        "name": "How To Make Pasta",
        "ingredients": "Pasta + Sauce"
    },
    ItemType.SALAD_DISH: {
        "name": "How To Make Salad",
        "ingredients": "Lettuce + Sauce"
    }
}
