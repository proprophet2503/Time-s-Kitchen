"""
Settings and constants for Time's Kitchen game
"""

# Screen settings
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650
FPS = 60
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

# Cooking times (in seconds)
COOK_TIME_MEAT = 5
COOK_TIME_SAUSAGE = 4
COOK_TIME_PASTA = 7

# Rewards (in dollars)
REWARD_BURGER = 10
REWARD_HOTDOG = 8
REWARD_PASTA = 6
REWARD_CLEANING = 3

# Orders per hour
ORDERS_PER_HOUR_SINGLE = 5
ORDERS_PER_HOUR_MULTI = 10

# Player settings
PLAYER_SPEED = 5
PLAYER_SIZE = 64

# Station settings
STATION_SIZE = 80

# Tile settings
TILE_SIZE = 64

# Item settings
ITEM_SIZE = 48

# Customer settings
CUSTOMER_SPEED = 3

# Dirt settings
DIRT_SPAWN_INTERVAL = 60  # Spawn dirt every 60 seconds (1 game hour)
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
    
    # Cooked ingredients
    COOKED_MEAT = "cooked_meat"
    COOKED_SAUSAGE = "cooked_sausage"
    BOILED_PASTA = "boiled_pasta"
    
    # Final dishes
    BURGER = "burger"
    HOTDOG = "hotdog"
    PASTA_DISH = "pasta_dish"

# Station types
class StationType:
    COOLER = "cooler"
    STOVE = "stove"
    BOILER = "boiler"
    ASSEMBLY = "assembly"
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
        "ingredients": [ItemType.BOILED_PASTA],
        "reward": REWARD_PASTA,
        "name": "Pasta"
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
