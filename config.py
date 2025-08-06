"""
Configuration settings for WoW Classic SoD Recipe Calculator
"""

import os
from pathlib import Path
from typing import Dict, Any

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# File paths
RECIPES_FILE = PROJECT_ROOT / "recipes.json"
MATERIALS_FILE = PROJECT_ROOT / "materials.json"
URLS_FILE = PROJECT_ROOT / "urls.txt"
FAILED_URLS_FILE = PROJECT_ROOT / "failed_urls.txt"
LOG_FILE = LOGS_DIR / "scraper.log"

# Scraper settings
SCRAPER_CONFIG = {
    "headless": True,
    "timeout": 15,
    "max_retries": 3,
    "delay": 2.0,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "chrome_options": [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-extensions",
        "--disable-plugins",
        "--disable-images",
        "--disable-javascript",
        "--disable-css",
        "--disable-animations",
        "--disable-web-security",
        "--disable-features=VizDisplayCompositor",
        "--memory-pressure-off",
        "--max_old_space_size=4096",
    ]
}

# Wowhead settings
WOWHEAD_CONFIG = {
    "base_url": "https://www.wowhead.com",
    "classic_url": "https://www.wowhead.com/classic",
    "api_endpoint": "https://www.wowhead.com/api",
    "rate_limit": 1.0,  # seconds between requests
    "max_concurrent": 1,  # max concurrent requests
}

# Web interface settings
WEB_CONFIG = {
    "port": 8000,
    "host": "localhost",
    "debug": True,
    "auto_reload": True,
    "cors_enabled": True,
}

# Data processing settings
DATA_CONFIG = {
    "backup_enabled": True,
    "backup_count": 5,
    "compression_enabled": False,
    "validation_enabled": True,
}

# Logging settings
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_handler": {
        "filename": str(LOG_FILE),
        "max_bytes": 10 * 1024 * 1024,  # 10MB
        "backup_count": 5,
    },
    "console_handler": {
        "level": "INFO",
    }
}

# Profession settings
PROFESSIONS = {
    "Alchemy": {
        "name": "Alchemy",
        "color": "#4ECDC4",
        "icon": "inv_potion_01",
        "specializations": ["Elixir Mastery", "Transmute Mastery"],
    },
    "Blacksmithing": {
        "name": "Blacksmithing", 
        "color": "#95A5A6",
        "icon": "inv_hammer_16",
        "specializations": [],
    },
    "Cooking": {
        "name": "Cooking",
        "color": "#E67E22",
        "icon": "inv_misc_food_01",
        "specializations": [],
    },
    "Enchanting": {
        "name": "Enchanting",
        "color": "#9B59B6",
        "icon": "inv_enchant_disenchant",
        "specializations": [],
    },
    "Engineering": {
        "name": "Engineering",
        "color": "#F39C12",
        "icon": "inv_gizmo_01",
        "specializations": ["Gnomish Engineering", "Goblin Engineering"],
    },
    "Leatherworking": {
        "name": "Leatherworking",
        "color": "#8B4513",
        "icon": "inv_misc_armorkit_17",
        "specializations": ["Dragonscale Leatherworking", "Elemental Leatherworking", "Tribal Leatherworking"],
    },
    "Tailoring": {
        "name": "Tailoring",
        "color": "#E91E63",
        "icon": "inv_fabric_linen_01",
        "specializations": ["Mooncloth Tailoring", "Shadoweave Tailoring", "Spellfire Tailoring"],
    },
}

# Item quality colors
QUALITY_COLORS = {
    "Poor": "#9D9D9D",
    "Common": "#FFFFFF", 
    "Uncommon": "#1EFF00",
    "Rare": "#0070DD",
    "Epic": "#A335EE",
    "Legendary": "#FF8000",
    "Artifact": "#E6CC80",
}

# Default vendor prices for common materials
DEFAULT_VENDOR_PRICES = {
    # Cooking materials
    2673: 2,    # Coyote Meat
    2674: 2,    # Crawler Meat
    2675: 2,    # Crawler Claw
    2677: 2,    # Boar Ribs
    2678: 2,    # Mild Spices
    2692: 2,    # Hot Spices
    2886: 2,    # Crag Boar Rib
    2924: 2,    # Crocolisk Meat
    3172: 2,    # Boar Intestines
    3173: 2,    # Bear Meat
    3174: 2,    # Spider Ichor
    3404: 2,    # Buzzard Wing
    3712: 2,    # Turtle Meat
    3730: 2,    # Big Bear Meat
    3731: 2,    # Lion Meat
    4603: 2,    # Raw Spotted Yellowtail
    4655: 2,    # Giant Clam Meat
    5465: 2,    # Small Spider Leg
    5466: 2,    # Scorpid Stinger
    5467: 2,    # Kodo Meat
    5468: 2,    # Soft Frenzy Flesh
    5469: 2,    # Strider Meat
    5470: 2,    # Thunder Lizard Tail
    5471: 2,    # Stag Meat
    5503: 2,    # Clam Meat
    5504: 2,    # Tangy Clam Meat
    6289: 2,    # Raw Longjaw Mud Snapper
    6291: 2,    # Raw Brilliant Smallfish
    6303: 2,    # Raw Slitherskin Mackerel
    6308: 2,    # Raw Bristle Whisker Catfish
    6317: 2,    # Raw Loch Frenzy
    6361: 2,    # Raw Rainbow Fin Albacore
    6362: 2,    # Raw Rockscale Cod
    6889: 2,    # Small Egg
    7097: 2,    # Leg Meat
    7290: 2,    # Pattern: Red Whelp Gloves
    7307: 2,    # Flesh Eating Worm
    7974: 2,    # Zesty Clam Meat
    8365: 2,    # Raw Mithril Head Trout
    8952: 2,    # Roasted Quail
    8953: 2,    # Deep Fried Plantains
    8957: 2,    # Spinefin Halibut
    1015: 2,    # Lean Wolf Flank
    1017: 2,    # Seasoned Wolf Kabob
    1080: 2,    # Tough Condor Meat
    1081: 2,    # Crisp Spider Meat
    1206: 2,    # Moss Agate
    1210: 2,    # Shadowgem
    12203: 2,   # Red Wolf Meat
    12204: 2,   # Heavy Kodo Meat
    12205: 2,   # White Spider Meat
    12206: 2,   # Tender Crab Meat
    12207: 2,   # Giant Egg
    12208: 2,   # Tender Wolf Meat
    12223: 2,   # Meaty Bat Wing
    12224: 2,   # Crisp Bat Wing
    12225: 2,   # Blump Family Fishing Pole
    12226: 2,   # Recipe: Crispy Bat Wing
    12227: 2,   # Recipe: Lean Wolf Steak
    12228: 2,   # Recipe: Roast Raptor
    12229: 2,   # Recipe: Hot Wolf Ribs
    12231: 2,   # Recipe: Jungle Stew
    12232: 2,   # Recipe: Carrion Surprise
    12233: 2,   # Recipe: Mystery Stew
    12239: 2,   # Recipe: Dragonbreath Chili
    12240: 2,   # Recipe: Heavy Kodo Stew
    13926: 2,   # Golden Pearl
    13927: 2,   # Cooked Glossy Mightfish
    13928: 2,   # Grilled Squid
    13929: 2,   # Hot Smoked Bass
    13930: 2,   # Filet of Redgill
    13931: 2,   # Nightfin Soup
    13932: 2,   # Poached Sunscale Salmon
    13933: 2,   # Lobster Stew
    13934: 2,   # Mightfish Steak
    13935: 2,   # Baked Salmon
    13936: 2,   # Delicious Chocolate Cake
    13937: 2,   # Spotted Yellowtail
    13938: 2,   # Transparent Scale
    13939: 2,   # Recipe: Spotted Yellowtail
    13940: 2,   # Recipe: Cooked Glossy Mightfish
    13941: 2,   # Recipe: Filet of Redgill
    13942: 2,   # Recipe: Grilled Squid
    13943: 2,   # Recipe: Hot Smoked Bass
    13945: 2,   # Recipe: Nightfin Soup
    13946: 2,   # Recipe: Poached Sunscale Salmon
    13947: 2,   # Recipe: Lobster Stew
    13948: 2,   # Recipe: Mightfish Steak
    13949: 2,   # Recipe: Baked Salmon
    13950: 2,   # Recipe: Spotted Yellowtail
    13951: 2,   # Recipe: Transparent Scale
    13952: 2,   # Recipe: Mightfish Steak
    13953: 2,   # Recipe: Baked Salmon
    13954: 2,   # Recipe: Spotted Yellowtail
    13955: 2,   # Recipe: Transparent Scale
    13956: 2,   # Recipe: Mightfish Steak
    13957: 2,   # Recipe: Baked Salmon
    13958: 2,   # Recipe: Spotted Yellowtail
    13959: 2,   # Recipe: Transparent Scale
    13960: 2,   # Recipe: Mightfish Steak
    13961: 2,   # Recipe: Baked Salmon
    13962: 2,   # Recipe: Spotted Yellowtail
    13963: 2,   # Recipe: Transparent Scale
    13964: 2,   # Recipe: Mightfish Steak
    13965: 2,   # Recipe: Baked Salmon
    13966: 2,   # Recipe: Spotted Yellowtail
    13967: 2,   # Recipe: Transparent Scale
    13968: 2,   # Recipe: Mightfish Steak
    13969: 2,   # Recipe: Baked Salmon
    13970: 2,   # Recipe: Spotted Yellowtail
    13971: 2,   # Recipe: Transparent Scale
    13972: 2,   # Recipe: Mightfish Steak
    13973: 2,   # Recipe: Baked Salmon
    13974: 2,   # Recipe: Spotted Yellowtail
    13975: 2,   # Recipe: Transparent Scale
    13976: 2,   # Recipe: Mightfish Steak
    13977: 2,   # Recipe: Baked Salmon
    13978: 2,   # Recipe: Spotted Yellowtail
    13979: 2,   # Recipe: Transparent Scale
    13980: 2,   # Recipe: Mightfish Steak
    13981: 2,   # Recipe: Baked Salmon
    13982: 2,   # Recipe: Spotted Yellowtail
    13983: 2,   # Recipe: Transparent Scale
    13984: 2,   # Recipe: Mightfish Steak
    13985: 2,   # Recipe: Baked Salmon
    13986: 2,   # Recipe: Spotted Yellowtail
    13987: 2,   # Recipe: Transparent Scale
    13988: 2,   # Recipe: Mightfish Steak
    13989: 2,   # Recipe: Baked Salmon
    13990: 2,   # Recipe: Spotted Yellowtail
    13991: 2,   # Recipe: Transparent Scale
    13992: 2,   # Recipe: Mightfish Steak
    13993: 2,   # Recipe: Baked Salmon
    13994: 2,   # Recipe: Spotted Yellowtail
    13995: 2,   # Recipe: Transparent Scale
    13996: 2,   # Recipe: Mightfish Steak
    13997: 2,   # Recipe: Baked Salmon
    13998: 2,   # Recipe: Spotted Yellowtail
    13999: 2,   # Recipe: Transparent Scale
    14000: 2,   # Recipe: Mightfish Steak
}

# Environment-specific settings
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    SCRAPER_CONFIG["headless"] = True
    WEB_CONFIG["debug"] = False
    LOGGING_CONFIG["level"] = "WARNING"
elif ENVIRONMENT == "testing":
    SCRAPER_CONFIG["headless"] = True
    WEB_CONFIG["debug"] = True
    LOGGING_CONFIG["level"] = "DEBUG"

# Export all settings
__all__ = [
    "PROJECT_ROOT",
    "DATA_DIR", 
    "LOGS_DIR",
    "RECIPES_FILE",
    "MATERIALS_FILE",
    "URLS_FILE",
    "FAILED_URLS_FILE",
    "LOG_FILE",
    "SCRAPER_CONFIG",
    "WOWHEAD_CONFIG",
    "WEB_CONFIG",
    "DATA_CONFIG",
    "LOGGING_CONFIG",
    "PROFESSIONS",
    "QUALITY_COLORS",
    "DEFAULT_VENDOR_PRICES",
    "ENVIRONMENT",
]