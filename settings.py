# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 120
TITLE = "Time's Kitchen"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
BROWN = (139, 69, 19)
DARK_BROWN = (101, 67, 33)

# UI Colors
UI_BG = (50, 50, 50)
UI_BORDER = (100, 100, 100)
ORDER_BG = (70, 50, 30)
ORDER_URGENT = (150, 50, 30)

# Game timing (in seconds)
GAME_DURATION = 360  # 6 minutes = 360 seconds
GAME_HOUR = 60  # 1 game hour = 60 real seconds (1 minute)
ORDER_TIMEOUT = 30  # Seconds before order expires

# Cooking times 
COOK_TIME_MEAT = 5
COOK_TIME_SAUSAGE = 4
COOK_TIME_PASTA = 7

# Rewards 
REWARD_BURGER = 10
REWARD_HOTDOG = 8
REWARD_PASTA = 6
REWARD_SALAD = 5
REWARD_CLEANING = 3

# Orders per hour
ORDERS_PER_HOUR_SINGLE = 5
ORDERS_PER_HOUR_MULTI = 10

# Player settings
PLAYER_SPEED = 2.7
PLAYER_SIZE = 80  
PLAYER1_SIZE = 120 

# Station settings
STATION_SIZE = 90

# Tile settings
TILE_SIZE = 200

# Item settings
ITEM_SIZE = 48

# Customer settings
CUSTOMER_SPEED = 3

# Dirt settings
DIRT_SPAWN_INTERVAL = 60  
MAX_DIRT_SPOTS = 5

# Asset paths
ASSETS_PATH = "assets/"

# Item types
class ItemType:
    # Raw ingredients
    BREAD = "bread"
    MEAT = "meat"
    SAUSAGE = "sausage"
    PASTA = "pasta"
    LETTUCE = "lettuce"  
    SAUCE = "sauce"  
    
    # Cooked ingredients
    COOKED_MEAT = "cooked_meat"
    COOKED_SAUSAGE = "cooked_sausage"
    BOILED_PASTA = "boiled_pasta"
    
    # Final dishes
    BURGER = "burger"
    HOTDOG = "hotdog"
    PASTA_DISH = "pasta_dish"
    SALAD_DISH = "salad_dish"
    
    # Tools
    MOP = "mop"

# Station types
class StationType:
    COOLER = "cooler"
    STOVE = "stove"
    BOILER = "boiler"
    ASSEMBLY = "assembly"
    SAUCE = "sauce"  
    SERVE = "serve"
    MOP = "mop"

# Recipes
RECIPES = {
    ItemType.BURGER: {
        "ingredients": [ItemType.BREAD, ItemType.COOKED_MEAT],
        "reward": REWARD_BURGER,
        "name": "Burger"
    },
    ItemType.HOTDOG: {
        "ingredients": [ItemType.BREAD, ItemType.COOKED_SAUSAGE],
        "reward": REWARD_HOTDOG,
        "name": "Hotdog"
    },
    ItemType.PASTA_DISH: {
        "ingredients": [ItemType.BOILED_PASTA, ItemType.SAUCE],
        "reward": REWARD_PASTA,
        "name": "Pasta"
    },
    ItemType.SALAD_DISH: {
        "ingredients": [ItemType.SAUCE, ItemType.LETTUCE],
        "reward": REWARD_SALAD,
        "name": "Salad"
    }
}

# Cooking mappings
COOKING_STOVE = {
    ItemType.MEAT: (ItemType.COOKED_MEAT, COOK_TIME_MEAT),
    ItemType.SAUSAGE: (ItemType.COOKED_SAUSAGE, COOK_TIME_SAUSAGE)
}

COOKING_BOILER = {
    ItemType.PASTA: (ItemType.BOILED_PASTA, COOK_TIME_PASTA)
}

# High score file
HIGHSCORE_FILE = "highscores.json"
