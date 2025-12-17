import pygame
import random
from settings import *
from sprites import Player, Customer, Cashier, DirtSpot, Mop, SpriteSheet, Pedestrian, Tenant, Storeboard, Bush
from stations import Cooler, Stove, Boiler, AssemblyTable, ServeCounter, MopStation, DiningTable, LongTable, IngredientTable, SauceStation, LettuceStation
from orders import OrderManager


class Kitchen:    
    def __init__(self, num_players=1, perks=None):
        self.num_players = num_players
        self.perks = perks if perks else {}
        
        # Load floor tile
        self.floor_tile = SpriteSheet.load_image("tile_floor.jpg", (TILE_SIZE, TILE_SIZE))
        self.wood_floor_tile = SpriteSheet.load_image("tile2.png", (TILE_SIZE, TILE_SIZE))
        
        # Load road image (large, single image)
        road_width = 400  
        road_height = SCREEN_HEIGHT - 70  
        self.road_image = SpriteSheet.load_image("road.png", (road_width, road_height))
        
        # Initialize sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.stations = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.customers = pygame.sprite.Group()
        self.dirt_spots = pygame.sprite.Group()
        self.dining_tables = pygame.sprite.Group()
        self.longtables = pygame.sprite.Group()
        self.pedestrians = pygame.sprite.Group()
        self.tenants = pygame.sprite.Group()
        self.storeboards = pygame.sprite.Group()
        self.bushes = pygame.sprite.Group()
        self.mops = pygame.sprite.Group()  
        
        # Create kitchen layout
        self._setup_stations()
        self._setup_players()
        self._setup_cashier()
        self._setup_pedestrians()
        self._setup_tenants()
        self._setup_storeboards()
        self._setup_bushes()
        self._setup_mops()
        
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
        # shows menu on click Cooler for meat/sausage 
        self.cooler = Cooler(5, 68, ItemType.MEAT) 
        
        # Ingredient tables for bread and pasta
        table_bread = IngredientTable(150, 290, ItemType.BREAD)
        table_pasta = IngredientTable(215, 290, ItemType.PASTA)

        self.stations.add(self.cooler, table_bread, table_pasta)
        self.all_sprites.add(self.cooler, table_bread, table_pasta)
        
        # Lettuce and Sauce stations for making salad 
        lettuce_station = LettuceStation(150, 470)
        sauce_station = SauceStation(215, 470)
        self.stations.add(lettuce_station, sauce_station)
        self.all_sprites.add(lettuce_station, sauce_station)
        
        # Cooler menu state
        self.show_cooler_menu = False
        self.cooler_menu_player = None 
        
        # Stoves for meat and sausage
        stove1 = Stove(125, 95)
        stove2 = Stove(220, 95)
        self.stations.add(stove1, stove2)
        self.all_sprites.add(stove1, stove2)
        self.stoves = [stove1, stove2]
        
        # Boilers for pasta  
        boiler1 = Boiler(325, 95)
        boiler2 = Boiler(415, 95)
        self.stations.add(boiler1, boiler2)
        self.all_sprites.add(boiler1, boiler2)
        self.boilers = [boiler1, boiler2]
        
        # Cashier Counter
        self.serve_counter = ServeCounter(550, 95)
        self.stations.add(self.serve_counter)
        self.all_sprites.add(self.serve_counter)
        
        # Assembly Tables
        assembly1 = AssemblyTable(475, 335)
        assembly2 = AssemblyTable(475, 390)
        self.stations.add(assembly1, assembly2)
        self.all_sprites.add(assembly1, assembly2)
        self.assembly_tables = [assembly1, assembly2]

        # MOP Station
        self.mop_station = MopStation(15, 580)
        self.stations.add(self.mop_station)
        self.all_sprites.add(self.mop_station)
        
        # Dining Tables 
        dining_positions = [
            (900, 220), (900, 320), (900, 420), 
            (750, 220), (750, 320), (750, 420) 
        ]
        for x, y in dining_positions:
            table = DiningTable(x, y)
            self.dining_tables.add(table)
            self.all_sprites.add(table)

        # Long tables
        longtable1 = LongTable(-25, 670, 550)  
        longtable2 = LongTable(450, 670, 158)  
        longtable3 = LongTable(550, 100, 415, vertical=True)  
        longtable4 = LongTable(550, 20, 100, vertical=True) 
        
        for lt in [longtable1, longtable2, longtable3, longtable4]:
            self.longtables.add(lt)
            self.all_sprites.add(lt)  

        # Customer spawn position
        self.customer_spawn_y = 95
        
        # Track cooking stations for dirt spawning
        self.cooking_stations = self.stoves + self.boilers
        
    def _setup_players(self):
        # Apply speed perk if purchased
        speed_boost = self.perks.get("speed_boost", 0)
        
        # Player 1 starts in kitchen area
        player1 = Player(1, 200, 200, speed_boost=speed_boost, 
                        holding_boost=self.perks.get("holding_boost", 0))
        self.players.add(player1)
        self.all_sprites.add(player1)
        
        if self.num_players == 2:
            # Player 2 starts nearby in kitchen
            player2 = Player(2, 250, 200, speed_boost=speed_boost,
                           holding_boost=self.perks.get("holding_boost", 0))
            self.players.add(player2)
            self.all_sprites.add(player2)
    
    def _setup_cashier(self):
        self.cashier = Cashier(500, 95)
    
    def _setup_pedestrians(self):
        road_start_x = SCREEN_WIDTH - 400  
        
        # Create 3-4 pedestrians at different positions walking in different directions
        pedestrian_positions = [
            (road_start_x + 100, 150, "down"),
            (road_start_x + 250, 300, "up"),
            (road_start_x + 150, 500, "down"),
            (road_start_x + 300, 100, "up"),
        ]
        
        for x, y, direction in pedestrian_positions:
            ped = Pedestrian(x, y, direction)
            self.pedestrians.add(ped)
            self.all_sprites.add(ped)
    
    def _setup_tenants(self):
        road_start_x = SCREEN_WIDTH - 70  
        
        # Place tenant 
        tenant = Tenant(road_start_x - 10, 145)
        tenant2 = Tenant(road_start_x - 130, 250)
        self.tenants.add(tenant)
        self.tenants.add(tenant2)
    
    def _setup_storeboards(self):
        road_start_x = SCREEN_WIDTH - 188  
        
        # Place storeboard 
        storeboard = Storeboard(road_start_x - 10, 420)
        self.storeboards.add(storeboard)
        self.all_sprites.add(storeboard)
    def _setup_bushes(self):
        road_start_x = SCREEN_WIDTH - 250 
        
        # Create multiple bushes 
        bush_positions = [
            (road_start_x - 450, 28, 85),
            (road_start_x - 450, 148, 120),   
            (road_start_x - 450, 200, 120),   
            (road_start_x - 450, 250, 120),   
            (road_start_x - 450, 300, 85),
            (road_start_x - 450, 350, 85),
            (road_start_x - 450, 400, 85),
            (road_start_x - 450, 420, 85),
            (road_start_x - 450, 665, 85),     
        ]
        
        for x, y, height in bush_positions:
            bush = Bush(x, y, height=height)
            self.bushes.add(bush)
            self.all_sprites.add(bush)
    
    def _setup_mops(self):
        mop1 = Mop(30, 595)
        self.mops.add(mop1)
    
    def _on_new_order(self, order):
        self.cashier.announce_order(order.name)
        
        # Find available dining table
        available_table = None
        for table in self.dining_tables:
            if not table.occupied:
                available_table = table
                table.occupied = True
                break
        
        # Calculate line position for new customer
        line_position = len([c for c in self.customers if c.state in ["arriving", "waiting", "going_to_table"]])
        
        # Spawn customer in waiting line
        target_x = self.serve_counter.rect.x + 80 + (line_position * 50)
        customer = Customer(
            target_x,
            self.serve_counter.rect.y + 20,
            order,
            line_position,
            available_table  
        )
        self.customers.add(customer)
        
        order.customer = customer
        order.dining_table = available_table
    
    def _update_customer_line(self):
        waiting_customers = [c for c in self.customers if c.state in ["arriving", "waiting"]]
        waiting_customers.sort(key=lambda c: c.line_position)
        
        for i, customer in enumerate(waiting_customers):
            new_x = self.serve_counter.rect.x + 80 + (i * 50)
            if customer.line_position != i or customer.target_x != new_x:
                customer.update_line_position(i, new_x)
    
    def _spawn_dirt(self):
        if len(self.dirt_spots) < MAX_DIRT_SPOTS and self.cooking_stations:
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
        self.message = msg
        self.message_timer = duration
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.show_cooler_menu:
                if event.key == pygame.K_1:
                    self._select_from_cooler(ItemType.MEAT, self.cooler_menu_player)
                    self.show_cooler_menu = False
                    self.cooler_menu_player = None
                    return
                elif event.key == pygame.K_2:
                    self._select_from_cooler(ItemType.SAUSAGE, self.cooler_menu_player)
                    self.show_cooler_menu = False
                    self.cooler_menu_player = None
                    return
                elif event.key == pygame.K_ESCAPE:
                    self.show_cooler_menu = False
                    self.cooler_menu_player = None
                    return
            
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
        players_list = list(self.players)
        if index < len(players_list):
            return players_list[index]
        return None
    
    def _player_interact(self, player_index):
        player = self._get_player(player_index)
        if not player:
            return
        
        # Check for mop pickup 
        for mop in self.mops:
            if not mop.is_held:
                distance = ((mop.rect.centerx - player.rect.centerx) ** 2 + 
                           (mop.rect.centery - player.rect.centery) ** 2) ** 0.5
                if distance < 80:
                    if player.pickup_mop(mop):
                        mop.is_held = True
                        mop.holder = player  
                        self.show_message("Picked up mop! Press SPACE near dirt to clean")
                        return
        
        # Check for dirt cleaning with mop
        if player.holding_mop:
            for dirt in self.dirt_spots:
                distance = ((dirt.rect.centerx - player.rect.centerx) ** 2 + 
                           (dirt.rect.centery - player.rect.centery) ** 2) ** 0.5
                if distance < 80:
                    # Start cleaning animation
                    if player.start_cleaning():
                        # Remove dirt after animation completes
                        reward = dirt.clean()
                        self.score += reward
                        self.show_message(f"+${reward} for cleaning!")
                        return
        
        # Check for cooler interaction (show menu)
        if self.cooler.can_interact(player):
            self.show_cooler_menu = True
            self.cooler_menu_player = player_index  
            return
        
        # Check for other station interactions
        for station in self.stations:
            if station != self.cooler and station.can_interact(player):
                success, msg = station.interact(player)
                if msg:
                    self.show_message(msg)
                return
        
        self.show_message("Nothing to interact with")
    
    def _player_serve(self, player_index):
        player = self._get_player(player_index)
        if not player:
            return
        
        # Check if player has a completed dish
        held_dish = None
        for item in player.held_items:
            if item.item_type in [ItemType.BURGER, ItemType.HOTDOG, ItemType.PASTA_DISH, ItemType.SALAD_DISH]:
                held_dish = item
                break
        
        if not held_dish:
            self.show_message("No dish to serve!")
            return
        
        # Check if near a customer at dining table
        for customer in self.customers:
            if customer.state == "sitting":
                distance = ((customer.rect.centerx - player.rect.centerx) ** 2 + 
                           (customer.rect.centery - player.rect.centery) ** 2) ** 0.5
                
                if distance < 80:  
                    if customer.can_receive_delivery(held_dish.item_type):
                        success, reward, completed_order = self.order_manager.try_fulfill_order(held_dish.item_type)
                        if success:
                            # Remove dish from player
                            player.held_items.remove(held_dish)
                            
                            # Customer receives order
                            customer.receive_delivery(held_dish.image)
                            
                            # Apply salary multiplier perk
                            salary_multiplier = self.perks.get("salary_multiplier", 1)
                            final_reward = reward * salary_multiplier
                            
                            # Update score
                            self.score += final_reward
                            self.show_message(f"Order delivered! +${final_reward}")
                            
                            # Update customer line positions
                            self._update_customer_line()
                            return
                        else:
                            self.show_message("Order already complete!")
                            return
                    else:
                        self.show_message("Wrong dish for this customer!")
                        return
        
        self.show_message("No customer nearby!")
    
    def _player_drop(self, player_index):
        player = self._get_player(player_index)
        if not player:
            return
        
        # Check if holding mop - drop it
        if player.holding_mop:
            mop = player.drop_mop()
            if mop:
                # Place mop at player's current position
                mop.rect.x = player.rect.x
                mop.rect.y = player.rect.y + player.rect.height
                mop.is_held = False
                mop.holder = None  
                self.show_message("Dropped mop")
                return
        
        # Otherwise drop held item
        dropped = player.drop_item()
        if dropped:
            self.show_message(f"Dropped {dropped.get_display_name()}")
        else:
            self.show_message("Nothing to drop")
    
    def _select_from_cooler(self, item_type, player_index=0):
        player = self._get_player(player_index)
        if not player:
            return
        
        if len(player.held_items) < 3:
            from sprites import Item
            new_item = Item(item_type)
            player.pickup_item(new_item)
            label = "Meat" if item_type == ItemType.MEAT else "Sausage"
            self.show_message(f"Picked up {label}")
        else:
            self.show_message("Hands full!")
    
    def update(self, dt):
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
        
        # Include stations, long tables, and dining tables as obstacles
        obstacles = [s for s in self.stations] + list(self.longtables) + list(self.dining_tables)
        for player in self.players:
            player.update(keys, obstacles)
        
        # Update cooking stations
        for station in self.stations:
            station.update(dt)
        
        # Update mops
        for mop in self.mops:
            mop.update()
        
        # Update orders
        self.order_manager.update(dt, self.time_remaining)
        
        # Update customers with dt
        for customer in self.customers:
            customer.update(dt)
        
        # Update pedestrians
        for pedestrian in self.pedestrians:
            pedestrian.update(dt)
        
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
        dining_area_x = 600 
        
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            for y in range(70, SCREEN_HEIGHT, TILE_SIZE):
                if x >= dining_area_x:
                    screen.blit(self.wood_floor_tile, (x, y))
                else:
                    screen.blit(self.floor_tile, (x, y))
        
        # Draw road on top of wood floor 
        road_x = SCREEN_WIDTH - 260  
        road_y = 120  
        screen.blit(self.road_image, (road_x, road_y))
        
        # Draw dining tables 
        for table in self.dining_tables:
            screen.blit(table.image, table.rect)

         # Draw long tables
        for longtable in self.longtables:
            screen.blit(longtable.image, longtable.rect)

        # Draw stations
        for station in self.stations:
            station.draw(screen)
        
        # Draw dirt spots
        for dirt in self.dirt_spots:
            screen.blit(dirt.image, dirt.rect)
        
        # Draw mops (not being held)
        for mop in self.mops:
            mop.draw(screen)
        
        # Draw customers
        for customer in self.customers:
            customer.draw(screen)
        
        # Draw tenants (decorations)
        for tenant in self.tenants:
            tenant.draw(screen)
        
        # Draw storeboards (decorations)
        for storeboard in self.storeboards:
            storeboard.draw(screen)
        
        # Draw bushes (decorations)
        for bush in self.bushes:
            bush.draw(screen)
        
        # Draw pedestrians
        for pedestrian in self.pedestrians:
            pedestrian.draw(screen)
        
        # Draw cashier
        self.cashier.draw(screen)
        
        # Draw players 
        for player in self.players:
            player.draw(screen)
        
        # Draw cooler menu if active
        if self.show_cooler_menu:
            self._draw_cooler_menu(screen)
    
    def _draw_cooler_menu(self, screen):
        WIDTH, HEIGHT = SCREEN_WIDTH, SCREEN_HEIGHT
        box_width, box_height = 500, 260
        box_x, box_y = WIDTH//2 - box_width//2, HEIGHT//2 - box_height//2
        
        # Shadow effect
        shadow = pygame.Surface((box_width + 10, box_height + 10), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 120), shadow.get_rect(), border_radius=20)
        screen.blit(shadow, (box_x - 5, box_y + 5))
        
        # Main menu box
        s = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(s, (40, 40, 40, 240), (0, 0, box_width, box_height), border_radius=20)
        pygame.draw.rect(s, (255, 220, 120), (0, 0, box_width, box_height), 3, border_radius=20)
        screen.blit(s, (box_x, box_y))
        
        # Title
        big_font = pygame.font.Font(None, 60)
        title = big_font.render("COOLER", True, (255, 240, 180))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, box_y + 25))
        pygame.draw.line(screen, (255, 220, 120), (box_x + 50, box_y + 75), (box_x + box_width - 50, box_y + 75), 2)
        
        # Menu options
        font = pygame.font.Font(None, 36)
        opt1 = font.render("1 Meat", True, (220, 220, 220))
        opt2 = font.render("2 Sausage", True, (220, 220, 220))
        screen.blit(opt1, (WIDTH//2 - opt1.get_width()//2, box_y + 110))
        screen.blit(opt2, (WIDTH//2 - opt2.get_width()//2, box_y + 150))
        
        # Hint text
        hint = font.render("Press 1 or 2 to pick, or ESC to cancel", True, (180, 180, 180))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, box_y + box_height - 50))
        
        # Glow effect
        glow_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (255, 240, 180, 40), (0, 0, box_width, box_height), border_radius=20)
        screen.blit(glow_surface, (box_x, box_y))
    
    def draw_orders(self, screen):
        self.order_manager.draw(screen, 0, 0)  
    
    def get_message(self):
        if self.message_timer > 0:
            alpha = min(255, self.message_timer * 4)
            return self.message, alpha
        return None, 0
    
    def is_game_over(self):
        return self.time_remaining <= 0
    
    def get_stats(self):
        return {
            'score': self.score,
            'time_remaining': self.time_remaining,
            'game_hour': self.game_hour,
            'orders_completed': self.order_manager.total_completed,
            'total_reward': self.order_manager.total_reward
        }
