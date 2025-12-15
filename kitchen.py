"""
Kitchen and gameplay management for Time's Kitchen game
"""

import pygame
import random
from settings import *
from sprites import Player, Customer, Cashier, DirtSpot, SpriteSheet
from stations import Cooler, Stove, Boiler, AssemblyTable, ServeCounter, MopStation, DiningTable
from orders import OrderManager


class Kitchen:
    """Main kitchen/gameplay area management"""
    
    def __init__(self, num_players=1):
        self.num_players = num_players
        
        # Load floor tile
        self.floor_tile = SpriteSheet.load_image("tile_floor.jpg", (TILE_SIZE, TILE_SIZE))
        
        # Initialize sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.stations = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.customers = pygame.sprite.Group()
        self.dirt_spots = pygame.sprite.Group()
        self.dining_tables = pygame.sprite.Group()
        
        # Create kitchen layout
        self._setup_stations()
        self._setup_players()
        self._setup_cashier()
        
        # Order management
        self.order_manager = OrderManager(num_players)
        self.order_manager.on_new_order = self._on_new_order
        
        # Game state
        self.score = 0
        self.time_remaining = GAME_DURATION
        self.game_hour = 1
        self.last_dirt_spawn = 0
        
        # Message display
        self.message = ""
        self.message_timer = 0
        
        # Customer spawn position (near serve counter)
        self.customer_spawn_y = 0
        
    def _setup_stations(self):
        """Set up all kitchen stations based on reference layout"""
        # Layout based on reference image:
        # Left side: Cooler (refrigerator) + ingredient shelves
        # Top center: Stove and Boiler for cooking
        # Right side: Serve counter with cashier
        # Middle: Assembly tables
        # Bottom: Dining tables
        
        # === LEFT SIDE - Ingredient Storage ===
        # Cooler (refrigerator) for each ingredient - vertical stack
        cooler_meat = Cooler(15, 95, ItemType.MEAT)
        cooler_bread = Cooler(15, 185, ItemType.BREAD)
        cooler_sausage = Cooler(15, 275, ItemType.SAUSAGE)
        cooler_pasta = Cooler(15, 365, ItemType.PASTA)
        
        self.stations.add(cooler_meat, cooler_bread, cooler_sausage, cooler_pasta)
        self.all_sprites.add(cooler_meat, cooler_bread, cooler_sausage, cooler_pasta)
        
        # === TOP CENTER - Cooking Area ===
        # Stoves for meat and sausage
        stove1 = Stove(130, 95)
        stove2 = Stove(220, 95)
        self.stations.add(stove1, stove2)
        self.all_sprites.add(stove1, stove2)
        self.stoves = [stove1, stove2]
        
        # Boilers for pasta  
        boiler1 = Boiler(330, 95)
        boiler2 = Boiler(420, 95)
        self.stations.add(boiler1, boiler2)
        self.all_sprites.add(boiler1, boiler2)
        self.boilers = [boiler1, boiler2]
        
        # === RIGHT SIDE - Serve Counter ===
        self.serve_counter = ServeCounter(530, 95)
        self.stations.add(self.serve_counter)
        self.all_sprites.add(self.serve_counter)
        
        # === MIDDLE - Assembly Tables ===
        assembly1 = AssemblyTable(150, 250)
        assembly2 = AssemblyTable(280, 250)
        self.stations.add(assembly1, assembly2)
        self.all_sprites.add(assembly1, assembly2)
        self.assembly_tables = [assembly1, assembly2]
        
        # === MOP Station ===
        self.mop_station = MopStation(420, 250)
        self.stations.add(self.mop_station)
        self.all_sprites.add(self.mop_station)
        
        # === BOTTOM - Dining Tables (decorative) ===
        dining_positions = [(130, 420), (300, 420), (470, 420)]
        for x, y in dining_positions:
            table = DiningTable(x, y)
            self.dining_tables.add(table)
            self.all_sprites.add(table)
        
        # Customer spawn position
        self.customer_spawn_y = 95
        
        # Track cooking stations for dirt spawning
        self.cooking_stations = self.stoves + self.boilers
        
    def _setup_players(self):
        """Set up player(s)"""
        # Player 1 starts in middle area
        player1 = Player(1, 280, 350)
        self.players.add(player1)
        self.all_sprites.add(player1)
        
        if self.num_players == 2:
            # Player 2 starts nearby
            player2 = Player(2, 400, 350)
            self.players.add(player2)
            self.all_sprites.add(player2)
    
    def _setup_cashier(self):
        """Set up the cashier NPC"""
        # Cashier stands next to serve counter
        self.cashier = Cashier(620, 95)
    
    def _on_new_order(self, order):
        """Callback when new order is created"""
        self.cashier.announce_order(order.name)
        
        # Calculate line position for new customer
        line_position = len([c for c in self.customers if c.state in ["arriving", "waiting"]])
        
        # Spawn customer in waiting line
        target_x = self.serve_counter.rect.x + 80 + (line_position * 50)
        customer = Customer(
            target_x,
            self.serve_counter.rect.y + 20,
            order,
            line_position
        )
        self.customers.add(customer)
    
    def _update_customer_line(self):
        """Update customer positions in the waiting line"""
        waiting_customers = [c for c in self.customers if c.state in ["arriving", "waiting"]]
        waiting_customers.sort(key=lambda c: c.line_position)
        
        for i, customer in enumerate(waiting_customers):
            new_x = self.serve_counter.rect.x + 80 + (i * 50)
            if customer.line_position != i or customer.target_x != new_x:
                customer.update_line_position(i, new_x)
    
    def _spawn_dirt(self):
        """Spawn dirt spots near cooking stations"""
        if len(self.dirt_spots) < MAX_DIRT_SPOTS and self.cooking_stations:
            # Choose random cooking station
            station = random.choice(self.cooking_stations)
            
            # Spawn dirt in front of station
            dirt_x = station.rect.x + random.randint(-30, 30)
            dirt_y = station.rect.bottom + random.randint(10, 50)
            
            # Make sure it's in valid area
            dirt_y = min(dirt_y, SCREEN_HEIGHT - 100)
            
            dirt = DirtSpot(dirt_x, dirt_y)
            self.dirt_spots.add(dirt)
            self.all_sprites.add(dirt)
            
            self.show_message("Kitchen is getting dirty!")
    
    def show_message(self, msg, duration=120):
        """Show a temporary message"""
        self.message = msg
        self.message_timer = duration
    
    def handle_input(self, event):
        """Handle player input events"""
        if event.type == pygame.KEYDOWN:
            # Player 1 controls
            if event.key == pygame.K_SPACE:
                self._player_interact(0)
            elif event.key == pygame.K_e:
                self._player_serve(0)
            elif event.key == pygame.K_q:
                self._player_drop(0)
            
            # Player 2 controls
            if self.num_players == 2:
                if event.key == pygame.K_RETURN:
                    self._player_interact(1)
                elif event.key == pygame.K_PERIOD:
                    self._player_serve(1)
                elif event.key == pygame.K_COMMA:
                    self._player_drop(1)
    
    def _get_player(self, index):
        """Get player by index"""
        players_list = list(self.players)
        if index < len(players_list):
            return players_list[index]
        return None
    
    def _player_interact(self, player_index):
        """Handle player interaction with stations"""
        player = self._get_player(player_index)
        if not player:
            return
        
        # Check for dirt cleaning first
        for dirt in self.dirt_spots:
            distance = ((dirt.rect.centerx - player.rect.centerx) ** 2 + 
                       (dirt.rect.centery - player.rect.centery) ** 2) ** 0.5
            if distance < 80:
                reward = dirt.clean()
                self.score += reward
                self.show_message(f"+${reward} for cleaning!")
                return
        
        # Check for station interaction
        for station in self.stations:
            if station.can_interact(player):
                success, msg = station.interact(player)
                if msg:
                    self.show_message(msg)
                return
        
        self.show_message("Nothing to interact with")
    
    def _player_serve(self, player_index):
        """Handle player serving a dish"""
        player = self._get_player(player_index)
        if not player:
            return
        
        # Check if near serve counter
        if self.serve_counter.can_interact(player):
            # Check if player has a completed dish
            for item in player.held_items:
                if item.item_type in [ItemType.BURGER, ItemType.HOTDOG, ItemType.PASTA_DISH]:
                    # Try to fulfill an order
                    success, reward, completed_order = self.order_manager.try_fulfill_order(item.item_type)
                    
                    if success:
                        player.held_items.remove(item)
                        self.score += reward
                        self.show_message(f"Order complete! +${reward}")
                        
                        # Make a waiting customer leave with food
                        for customer in self.customers:
                            if customer.is_waiting() and customer.order and customer.order.order_id == completed_order.order_id:
                                customer.serve(item.image)
                                break
                        else:
                            # Fallback: first waiting customer
                            for customer in self.customers:
                                if customer.is_waiting():
                                    customer.serve(item.image)
                                    break
                        
                        # Update customer line positions
                        self._update_customer_line()
                        return
                    else:
                        self.show_message("No matching order!")
                        return
            
            self.show_message("No dish to serve!")
        else:
            self.show_message("Go to serve counter!")
    
    def _player_drop(self, player_index):
        """Handle player dropping an item"""
        player = self._get_player(player_index)
        if not player:
            return
        
        dropped = player.drop_item()
        if dropped:
            self.show_message(f"Dropped {dropped.get_display_name()}")
        else:
            self.show_message("Nothing to drop")
    
    def update(self, dt):
        """Update all game elements"""
        # Update time
        self.time_remaining -= dt
        if self.time_remaining < 0:
            self.time_remaining = 0
        
        # Calculate current game hour
        elapsed = GAME_DURATION - self.time_remaining
        self.game_hour = min(6, int(elapsed // GAME_HOUR) + 1)
        
        # Spawn dirt every game hour
        current_dirt_time = int(elapsed // GAME_HOUR)
        if current_dirt_time > self.last_dirt_spawn:
            self.last_dirt_spawn = current_dirt_time
            self._spawn_dirt()
        
        # Get pressed keys
        keys = pygame.key.get_pressed()
        
        # Update players
        obstacles = [s for s in self.stations]
        for player in self.players:
            player.update(keys, obstacles)
        
        # Update cooking stations
        for station in self.stations:
            station.update(dt)
        
        # Update orders
        self.order_manager.update(dt, self.time_remaining)
        
        # Update customers
        self.customers.update()
        
        # Update customer line positions
        self._update_customer_line()
        
        # Update cashier
        self.cashier.update()
        
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message = ""
    
    def draw(self, screen):
        """Draw the kitchen"""
        # Draw floor tiles starting after top bar
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            for y in range(70, SCREEN_HEIGHT, TILE_SIZE):
                screen.blit(self.floor_tile, (x, y))
        
        # Draw dining tables first (background)
        for table in self.dining_tables:
            screen.blit(table.image, table.rect)
        
        # Draw stations
        for station in self.stations:
            station.draw(screen)
        
        # Draw dirt spots
        for dirt in self.dirt_spots:
            screen.blit(dirt.image, dirt.rect)
        
        # Draw customers with their draw method
        for customer in self.customers:
            customer.draw(screen)
        
        # Draw cashier
        self.cashier.draw(screen)
        
        # Draw players (on top of everything)
        for player in self.players:
            player.draw(screen)
    
    def draw_orders(self, screen):
        """Draw the order queue in top bar"""
        self.order_manager.draw(screen, 0, 0)  # Orders drawn in top bar
    
    def get_message(self):
        """Get current message and alpha for display"""
        if self.message_timer > 0:
            alpha = min(255, self.message_timer * 4)
            return self.message, alpha
        return None, 0
    
    def is_game_over(self):
        """Check if game is over"""
        return self.time_remaining <= 0
    
    def get_stats(self):
        """Get game statistics"""
        return {
            'score': self.score,
            'time_remaining': self.time_remaining,
            'game_hour': self.game_hour,
            'orders_completed': self.order_manager.total_completed,
            'total_reward': self.order_manager.total_reward
        }
