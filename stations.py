"""
Station classes for Time's Kitchen game
"""

import pygame
from settings import *
from sprites import SpriteSheet, Item


class Station(pygame.sprite.Sprite):
    """Base class for all kitchen stations"""
    
    def __init__(self, station_type, x, y, image_file):
        super().__init__()
        self.station_type = station_type
        self.image = SpriteSheet.load_image(image_file, (STATION_SIZE, STATION_SIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Collision rect - tidak termasuk area tulisan di bawah
        # Hanya objek image saja yang punya collision, diperkecil sedikit
        collision_offset = 5  # Offset untuk memperkecil collision area
        self.collision_rect = pygame.Rect(
            self.rect.x + collision_offset,
            self.rect.y + collision_offset,
            self.rect.width - (collision_offset * 2),
            self.rect.height - (collision_offset * 2)
        )
        
        # Item on this station
        self.current_item = None
        
    def can_interact(self, player):
        """Player can interact only when touching the station"""
        return self.collision_rect.colliderect(player.rect)
    
    def interact(self, player):
        """Interact with this station - override in subclasses"""
        pass
    
    def update(self, dt=1/60):
        """Update station state - override in subclasses"""
        pass
    
    def draw(self, screen):
        """Draw the station and any items on it"""
        screen.blit(self.image, self.rect)
        if self.current_item:
            item_x = self.rect.centerx - ITEM_SIZE // 2
            item_y = self.rect.top - ITEM_SIZE // 2
            screen.blit(self.current_item.image, (item_x, item_y))


class Cooler(Station):
    """Station to get raw ingredients"""
    
    AVAILABLE_ITEMS = [ItemType.BREAD, ItemType.MEAT, ItemType.SAUSAGE, ItemType.PASTA]
    
    # Different images for different items (optional visual distinction)
    ITEM_IMAGES = {
        ItemType.BREAD: "bread.png",
        ItemType.MEAT: "meat.png", 
        ItemType.SAUSAGE: "sausage.png",
        ItemType.PASTA: "pasta.png"
    }
    
    def __init__(self, x, y, item_type):
        # Override image size for cooler (make it bigger)
        super().__init__(StationType.COOLER, x, y, "cooler.png")
        
        # Resize cooler to be bigger (120x120 instead of default STATION_SIZE)
        cooler_size = 120
        self.image = SpriteSheet.load_image("cooler.png", (cooler_size, cooler_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Update collision rect
        self.collision_rect = pygame.Rect(
            self.rect.x,
            self.rect.y,
            self.rect.width,
            self.rect.height
        )
        
        self.provides_item = item_type
        self.label = self._get_label()
        
        # Load preview image for this ingredient
        preview_file = self.ITEM_IMAGES.get(item_type, "bread.png")
        self.preview_image = SpriteSheet.load_image(preview_file, (40, 40))  # Bigger preview too
        
    def _get_label(self):
        """Get label for this cooler"""
        labels = {
            ItemType.BREAD: "Bread",
            ItemType.MEAT: "Meat",
            ItemType.SAUSAGE: "Sausage",
            ItemType.PASTA: "Pasta"
        }
        return labels.get(self.provides_item, "?")
    
    def interact(self, player):
        """Give player an ingredient"""
        if len(player.held_items) < 3:
            new_item = Item(self.provides_item)
            player.pickup_item(new_item)
            return True, f"Picked up {self.label}"
        return False, "Hands full!"
    
    def draw(self, screen):
        """Draw cooler with label and preview"""
        screen.blit(self.image, self.rect)
        
        # Draw ingredient preview on cooler
        preview_x = self.rect.centerx - 20  # Adjusted for bigger preview
        preview_y = self.rect.centery - 20
        screen.blit(self.preview_image, (preview_x, preview_y))
        
        # Draw label with background
        font = pygame.font.Font(None, 18)
        text = font.render(self.label, True, WHITE)
        text_rect = text.get_rect(centerx=self.rect.centerx, top=self.rect.bottom + 2)
        
        # Background for better visibility
        bg_rect = text_rect.inflate(8, 4)
        pygame.draw.rect(screen, (40, 40, 40), bg_rect)
        pygame.draw.rect(screen, (100, 100, 100), bg_rect, 1)
        screen.blit(text, text_rect)


class CookingStation(Station):
    """Base class for cooking stations (Stove, Boiler)"""
    
    def __init__(self, station_type, x, y, image_file, recipes, label=""):
        super().__init__(station_type, x, y, image_file)
        self.recipes = recipes  # Dict of input_item: (output_item, cook_time)
        self.cooking = False
        self.cook_timer = 0
        self.cook_duration = 0
        self.output_item_type = None
        self.label = label
        
    def interact(self, player):
        """Place item to cook or pick up cooked item"""
        # If cooking is done, pick up the result
        if self.current_item and not self.cooking:
            if len(player.held_items) < 3:
                player.pickup_item(self.current_item)
                result_name = self.current_item.get_display_name()
                self.current_item = None
                return True, f"Picked up {result_name}"
            return False, "Hands full!"
        
        # If not cooking and no item, try to place an item
        if not self.cooking and not self.current_item:
            for item in player.held_items:
                if item.item_type in self.recipes:
                    # Start cooking - remove item from player
                    player.held_items.remove(item)
                    self.current_item = item
                    output_type, cook_time = self.recipes[item.item_type]
                    self.output_item_type = output_type
                    self.cook_duration = cook_time
                    self.cook_timer = 0
                    self.cooking = True
                    return True, f"Cooking {item.get_display_name()}... ({int(cook_time)}s)"
            return False, "No cookable items!"
        
        if self.cooking:
            remaining = self.cook_duration - self.cook_timer
            return False, f"Cooking... {remaining:.1f}s left"
        
        return False, "Station busy"
    
    def update(self, dt=1/60):
        """Update cooking progress"""
        if self.cooking:
            self.cook_timer += dt
            if self.cook_timer >= self.cook_duration:
                # Cooking complete
                self.cooking = False
                self.current_item = Item(self.output_item_type)
                self.output_item_type = None
                
    def draw(self, screen):
        """Draw station with cooking progress and label"""
        screen.blit(self.image, self.rect)
        
        # Draw item on station
        if self.current_item:
            item_x = self.rect.centerx - ITEM_SIZE // 2
            item_y = self.rect.centery - ITEM_SIZE // 2
            screen.blit(self.current_item.image, (item_x, item_y))
        
        # Draw label
        font = pygame.font.Font(None, 18)
        text = font.render(self.label, True, WHITE)
        text_rect = text.get_rect(centerx=self.rect.centerx, top=self.rect.bottom + 2)
        
        # Label background
        bg_rect = text_rect.inflate(6, 2)
        pygame.draw.rect(screen, (40, 40, 40), bg_rect)
        screen.blit(text, text_rect)
        
        # Draw cooking progress bar
        if self.cooking:
            bar_width = STATION_SIZE - 10
            bar_height = 10
            bar_x = self.rect.x + 5
            bar_y = self.rect.bottom + 18
            
            # Background
            pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
            
            # Progress
            progress = self.cook_timer / self.cook_duration
            color = GREEN if progress < 0.7 else (YELLOW if progress < 0.9 else ORANGE)
            pygame.draw.rect(screen, color, (bar_x, bar_y, int(bar_width * progress), bar_height))
            
            # Border
            pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
            
            # Timer text
            remaining = self.cook_duration - self.cook_timer
            timer_font = pygame.font.Font(None, 16)
            timer_text = timer_font.render(f"{remaining:.1f}s", True, WHITE)
            screen.blit(timer_text, (bar_x + bar_width + 5, bar_y))
        
        # Show "READY!" when cooked
        elif self.current_item:
            ready_font = pygame.font.Font(None, 20)
            ready_text = ready_font.render("READY!", True, GREEN)
            ready_rect = ready_text.get_rect(centerx=self.rect.centerx, top=self.rect.bottom + 18)
            screen.blit(ready_text, ready_rect)


class Stove(CookingStation):
    """Stove for cooking meat and sausage"""
    
    def __init__(self, x, y):
        super().__init__(StationType.STOVE, x, y, "stove.png", COOKING_STOVE, "Stove")


class Boiler(CookingStation):
    """Boiler for cooking pasta"""
    
    def __init__(self, x, y):
        super().__init__(StationType.BOILER, x, y, "boiler.png", COOKING_BOILER, "Boiler")


class AssemblyTable(Station):
    """Table for assembling dishes"""
    
    def __init__(self, x, y):
        super().__init__(StationType.ASSEMBLY, x, y, "assemble.png")
        self.items_on_table = []
        
    def interact(self, player):
        """Place items or assemble dishes"""
        # Try to assemble first
        assembled = self._try_assemble()
        if assembled:
            if len(player.held_items) < 3:
                player.pickup_item(assembled)
                return True, f"Made {assembled.get_display_name()}!"
            else:
                # Put assembled item on table
                self.current_item = assembled
                return True, f"Made {assembled.get_display_name()}! (on table)"
        
        # If there's a finished item on table, pick it up
        if self.current_item:
            if len(player.held_items) < 3:
                player.pickup_item(self.current_item)
                result_name = self.current_item.get_display_name()
                self.current_item = None
                return True, f"Picked up {result_name}"
            return False, "Hands full!"
        
        # Check if there are finished dishes on table that can be picked up
        for item in self.items_on_table:
            if item.item_type in [ItemType.BURGER, ItemType.HOTDOG, ItemType.PASTA_DISH, ItemType.SALAD_DISH]:
                if len(player.held_items) < 3:
                    player.pickup_item(item)
                    self.items_on_table.remove(item)
                    return True, f"Picked up {item.get_display_name()}"
                return False, "Hands full!"
        
        # Place item on table
        if player.held_items:
            item = player.held_items.pop()
            self.items_on_table.append(item)
            return True, f"Placed {item.get_display_name()} on table"
        
        return False, "Nothing to do"
    
    def _try_assemble(self):
        """Try to assemble items into a dish"""
        table_items = [item.item_type for item in self.items_on_table]
        
        for dish_type, recipe in RECIPES.items():
            recipe_items = recipe["ingredients"].copy()
            
            # Check if we have all required items
            can_make = True
            for ingredient in recipe_items:
                if ingredient not in table_items:
                    can_make = False
                    break
            
            if can_make:
                # Remove used items
                for ingredient in recipe_items:
                    for i, item in enumerate(self.items_on_table):
                        if item.item_type == ingredient:
                            self.items_on_table.pop(i)
                            break
                
                return Item(dish_type)
        
        return None
    
    def draw(self, screen):
        """Draw assembly table with items and label"""
        screen.blit(self.image, self.rect)
        
        # Draw label
        font = pygame.font.Font(None, 18)
        text = font.render("Assembly", True, WHITE)
        text_rect = text.get_rect(centerx=self.rect.centerx, top=self.rect.bottom + 2)
        bg_rect = text_rect.inflate(6, 2)
        pygame.draw.rect(screen, (40, 40, 40), bg_rect)
        screen.blit(text, text_rect)
        
        # Draw items on table
        for i, item in enumerate(self.items_on_table[:4]):  # Max 4 visible
            offset_x = (i % 2) * 30 - 15
            offset_y = (i // 2) * 30 - 15
            item_x = self.rect.centerx - ITEM_SIZE // 2 + offset_x
            item_y = self.rect.centery - ITEM_SIZE // 2 + offset_y
            screen.blit(item.image, (item_x, item_y))


class IngredientTable(Station):
    """Table for ingredient storage (bread, pasta, lettuce)"""
    
    ITEM_IMAGES = {
        ItemType.BREAD: "bread.png",
        ItemType.PASTA: "pasta.png",
        ItemType.LETTUCE: "lettuce.png"
    }
    
    def __init__(self, x, y, item_type):
        super().__init__(StationType.ASSEMBLY, x, y, "assemble.png")
        self.provides_item = item_type
        self.label = self._get_label()
        
        # Load preview image for this ingredient (bigger size)
        from sprites import SpriteSheet
        preview_file = self.ITEM_IMAGES.get(item_type, "bread.png")
        self.preview_image = SpriteSheet.load_image(preview_file, (50, 50))  # Increased from 32 to 50
    
    def _get_label(self):
        """Get label for this table"""
        labels = {
            ItemType.BREAD: "Bread",
            ItemType.PASTA: "Pasta",
            ItemType.LETTUCE: "Lettuce"
        }
        return labels.get(self.provides_item, "?")
    
    def interact(self, player):
        """Give player an ingredient from the table"""
        if len(player.held_items) < 3:
            new_item = Item(self.provides_item)
            player.pickup_item(new_item)
            return True, f"Picked up {self.label}"
        return False, "Hands full!"
    
    def draw(self, screen):
        """Draw ingredient table with label and preview"""
        screen.blit(self.image, self.rect)
        
        # Draw ingredient preview on table (centered)
        preview_x = self.rect.centerx - 25  # Adjusted for 50x50 size
        preview_y = self.rect.centery - 38  # Moved up by 10 pixels
        screen.blit(self.preview_image, (preview_x, preview_y))
        
        # Draw label with background
        font = pygame.font.Font(None, 18)
        text = font.render(self.label, True, WHITE)
        text_rect = text.get_rect(centerx=self.rect.centerx, top=self.rect.bottom + 2)
        
        # Background for better visibility
        bg_rect = text_rect.inflate(8, 4)
        pygame.draw.rect(screen, (40, 40, 40), bg_rect)
        pygame.draw.rect(screen, (100, 100, 100), bg_rect, 1)
        screen.blit(text, text_rect)

        # Draw assembled item if present
        if self.current_item:
            item_x = self.rect.centerx - ITEM_SIZE // 2
            item_y = self.rect.top - ITEM_SIZE - 5
            
            # Highlight ready dish
            pygame.draw.circle(screen, GREEN, 
                             (item_x + ITEM_SIZE//2, item_y + ITEM_SIZE//2), 
                             ITEM_SIZE//2 + 3, 2)
            screen.blit(self.current_item.image, (item_x, item_y))
            
            # Ready text
            ready_font = pygame.font.Font(None, 18)
            ready_text = ready_font.render("READY!", True, GREEN)
            ready_rect = ready_text.get_rect(centerx=self.rect.centerx, top=self.rect.bottom + 18)
            screen.blit(ready_text, ready_rect)


class ServeCounter(Station):
    """Counter to serve finished dishes to customers"""
    
    def __init__(self, x, y):
        super().__init__(StationType.SERVE, x, y, "serve.png")
        self.served_dish = None
        
    def interact(self, player):
        """Place a finished dish to serve or pick up from counter"""
        # If there's a dish on counter, pick it up
        if self.served_dish:
            if len(player.held_items) < 3:
                player.pickup_item(self.served_dish)
                result_name = self.served_dish.get_display_name()
                self.served_dish = None
                return True, f"Picked up {result_name}"
            return False, "Hands full!"
        
        # Check if player has a finished dish to serve
        for item in player.held_items:
            if item.item_type in [ItemType.BURGER, ItemType.HOTDOG, ItemType.PASTA_DISH, ItemType.SALAD_DISH]:
                player.held_items.remove(item)
                self.served_dish = item
                return True, f"Served {item.get_display_name()}"
        
        return False, "No dish to serve!"
    
    def draw(self, screen):
        """Draw serve counter with label"""
        screen.blit(self.image, self.rect)
        
        # Draw label
        font = pygame.font.Font(None, 18)
        text = font.render("Serve", True, WHITE)
        text_rect = text.get_rect(centerx=self.rect.centerx, top=self.rect.bottom + 2)
        bg_rect = text_rect.inflate(6, 2)
        pygame.draw.rect(screen, (40, 40, 40), bg_rect)
        screen.blit(text, text_rect)
        
        # Draw served dish
        if self.served_dish:
            item_x = self.rect.centerx - ITEM_SIZE // 2
            item_y = self.rect.centery - ITEM_SIZE // 2
            screen.blit(self.served_dish.image, (item_x, item_y))
    
    def get_served_dish(self):
        """Get and clear the served dish"""
        dish = self.served_dish
        self.served_dish = None
        return dish


class MopStation(Station):
    """Station to get mop for cleaning"""
    
    def __init__(self, x, y):
        # Use smaller size for mop (60x60 instead of default STATION_SIZE)
        super().__init__(StationType.MOP, x, y, "mop.png")
        mop_size = 60
        self.image = SpriteSheet.load_image("mop.png", (mop_size, mop_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Update collision rect
        self.collision_rect = pygame.Rect(
            self.rect.x,
            self.rect.y,
            self.rect.width,
            self.rect.height
        )
        
        self.has_mop = True
        
    def interact(self, player):
        """Player interacts to toggle mop holding"""
        # This station represents a mop location
        # When player has mop (special state), they can clean dirt
        return True, "Ready to clean! Walk to dirt spots."
    
    def draw(self, screen):
        """Draw mop station with label"""
        screen.blit(self.image, self.rect)
        
        # Draw label
        font = pygame.font.Font(None, 18)
        text = font.render("Mop", True, WHITE)
        text_rect = text.get_rect(centerx=self.rect.centerx, top=self.rect.bottom + 2)
        bg_rect = text_rect.inflate(6, 2)
        pygame.draw.rect(screen, (40, 40, 40), bg_rect)
        screen.blit(text, text_rect)
    
    def can_clean(self, player, dirt_spots):
        """Check if player can clean any nearby dirt"""
        for dirt in dirt_spots:
            distance = ((dirt.rect.centerx - player.rect.centerx) ** 2 + 
                       (dirt.rect.centery - player.rect.centery) ** 2) ** 0.5
            if distance < 60:
                return dirt
        return None


class LettuceStation(Station):
    """Station to get lettuce for making salad"""
    
    def __init__(self, x, y):
        super().__init__("lettuce", x, y, "assemble.png")
        
        # Load lettuce preview image
        from sprites import SpriteSheet
        self.preview_image = SpriteSheet.load_image("lettuce.png", (50, 50))
        
    def interact(self, player):
        """Pick up lettuce"""
        if len(player.held_items) < 3:
            from sprites import Item
            lettuce = Item(ItemType.LETTUCE, self.rect.x, self.rect.y)
            player.pickup_item(lettuce)
            return True, "Picked up Lettuce"
        return False, "Hands full!"
    
    def draw(self, screen):
        """Draw lettuce station with preview and label"""
        screen.blit(self.image, self.rect)
        
        # Draw preview image on table
        preview_x = self.rect.centerx - 25
        preview_y = self.rect.centery - 25
        screen.blit(self.preview_image, (preview_x, preview_y))
        
        # Draw label
        font = pygame.font.Font(None, 18)
        text = font.render("Lettuce", True, WHITE)
        text_rect = text.get_rect(centerx=self.rect.centerx, top=self.rect.bottom + 2)
        bg_rect = text_rect.inflate(6, 2)
        pygame.draw.rect(screen, (40, 40, 40), bg_rect)
        screen.blit(text, text_rect)


class SauceStation(Station):
    """Station to get sauce for making salad"""
    
    def __init__(self, x, y):
        super().__init__(StationType.SAUCE, x, y, "assemble.png")
        
        # Load sauce preview image
        from sprites import SpriteSheet
        self.preview_image = SpriteSheet.load_image("sauce.png", (50, 50))
        
    def interact(self, player):
        """Pick up sauce"""
        if len(player.held_items) < 3:
            from sprites import Item
            sauce = Item(ItemType.SAUCE, self.rect.x, self.rect.y)
            player.pickup_item(sauce)
            return True, "Picked up Sauce"
        return False, "Hands full!"
    
    def draw(self, screen):
        """Draw sauce station with preview and label"""
        screen.blit(self.image, self.rect)
        
        # Draw preview image on table
        preview_x = self.rect.centerx - 25
        preview_y = self.rect.centery - 25
        screen.blit(self.preview_image, (preview_x, preview_y))
        
        # Draw label
        font = pygame.font.Font(None, 18)
        text = font.render("Sauce", True, WHITE)
        text_rect = text.get_rect(centerx=self.rect.centerx, top=self.rect.bottom + 2)
        bg_rect = text_rect.inflate(6, 2)
        pygame.draw.rect(screen, (40, 40, 40), bg_rect)
        screen.blit(text, text_rect)


class DiningTable(Station):
    """Decorative dining table - customers sit here"""
    
    def __init__(self, x, y):
        super().__init__("dining", x, y, "diningtable.png")
        self.occupied = False  # Track if table is occupied by customer
        
    def interact(self, player):
        """No interaction with dining tables"""
        return False, "This is a customer dining table."
    
    def can_interact(self, player):
        """Dining tables don't have direct interaction"""
        return False
    
class LongTable(Station):
    """Decorative long table for kitchen"""
    
    def __init__(self, x, y, width=None, vertical=False):
        # Load image dengan custom width jika diberikan
        if width:
            base_img = SpriteSheet.load_image("longtable.png", (width, 64))
        else:
            base_img = SpriteSheet.load_image("longtable.png", None)
        
        # Rotate if vertical
        if vertical:
            self.image = pygame.transform.rotate(base_img, 90)
        else:
            self.image = base_img
        
        # Inisialisasi base Station tanpa load image lagi
        pygame.sprite.Sprite.__init__(self)
        self.station_type = "longtable"
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Collision rect - hanya objek, tidak termasuk label
        self.collision_rect = pygame.Rect(
            self.rect.x,
            self.rect.y,
            self.rect.width,
            self.rect.height
        )
        
        self.current_item = None
        
    def interact(self, player):
        """No interaction with long tables"""
        return False, "This is a decorative long table."
    
    def can_interact(self, player):
        """Long tables don't have direct interaction"""
        return False
