"""
Utility functions for WoW Classic SoD Recipe Calculator
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from config import (
    RECIPES_FILE, MATERIALS_FILE, DEFAULT_VENDOR_PRICES,
    PROFESSIONS, QUALITY_COLORS, DATA_CONFIG
)

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates recipe and material data structures."""
    
    @staticmethod
    def validate_recipe(recipe: Dict[str, Any]) -> bool:
        """Validate recipe data structure."""
        required_fields = [
            'recipe_id', 'name', 'profession', 'skill_level',
            'materials', 'result_item_id', 'result_quantity'
        ]
        
        for field in required_fields:
            if field not in recipe:
                logger.error(f"Missing required field '{field}' in recipe")
                return False
        
        # Validate data types
        if not isinstance(recipe['recipe_id'], int):
            logger.error("recipe_id must be an integer")
            return False
        
        if not isinstance(recipe['name'], str) or not recipe['name']:
            logger.error("name must be a non-empty string")
            return False
        
        if not isinstance(recipe['materials'], list):
            logger.error("materials must be a list")
            return False
        
        # Validate materials structure
        for material in recipe['materials']:
            if not DataValidator.validate_material(material):
                return False
        
        return True
    
    @staticmethod
    def validate_material(material: Dict[str, Any]) -> bool:
        """Validate material data structure."""
        required_fields = ['itemId', 'quantity']
        
        for field in required_fields:
            if field not in material:
                logger.error(f"Missing required field '{field}' in material")
                return False
        
        if not isinstance(material['itemId'], int):
            logger.error("itemId must be an integer")
            return False
        
        if not isinstance(material['quantity'], int) or material['quantity'] <= 0:
            logger.error("quantity must be a positive integer")
            return False
        
        return True
    
    @staticmethod
    def validate_materials_data(materials: Dict[str, Any]) -> bool:
        """Validate materials price data structure."""
        for item_id, item_data in materials.items():
            if not isinstance(item_id, str) or not item_id.isdigit():
                logger.error(f"Invalid item ID: {item_id}")
                return False
            
            if not isinstance(item_data, dict):
                logger.error(f"Invalid item data structure for {item_id}")
                return False
            
            required_fields = ['name', 'price']
            for field in required_fields:
                if field not in item_data:
                    logger.error(f"Missing required field '{field}' in item {item_id}")
                    return False
        
        return True


class DataProcessor:
    """Processes and transforms recipe and material data."""
    
    @staticmethod
    def calculate_recipe_cost(recipe: Dict[str, Any], materials_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate the total cost of crafting a recipe."""
        total_cost = 0.0
        material_costs = []
        
        for material in recipe.get('materials', []):
            item_id = str(material['itemId'])
            quantity = material['quantity']
            
            if item_id in materials_data:
                item_price = materials_data[item_id].get('price', 0)
                material_cost = item_price * quantity
                total_cost += material_cost
                
                material_costs.append({
                    'itemId': material['itemId'],
                    'name': materials_data[item_id].get('name', 'Unknown'),
                    'quantity': quantity,
                    'unit_price': item_price,
                    'total_cost': material_cost
                })
            else:
                # Use vendor price as fallback
                vendor_price = DEFAULT_VENDOR_PRICES.get(material['itemId'], 0)
                material_cost = vendor_price * quantity
                total_cost += material_cost
                
                material_costs.append({
                    'itemId': material['itemId'],
                    'name': 'Unknown',
                    'quantity': quantity,
                    'unit_price': vendor_price,
                    'total_cost': material_cost,
                    'vendor_price': True
                })
        
        return {
            'total_cost': total_cost,
            'material_costs': material_costs,
            'material_count': len(recipe.get('materials', []))
        }
    
    @staticmethod
    def calculate_recipe_profit(recipe: Dict[str, Any], materials_data: Dict[str, Any], 
                              result_price: float = 0.0) -> Dict[str, float]:
        """Calculate profit for a recipe."""
        cost_data = DataProcessor.calculate_recipe_cost(recipe, materials_data)
        total_cost = cost_data['total_cost']
        
        # Calculate result value
        result_quantity = recipe.get('result_quantity', 1)
        total_result_value = result_price * result_quantity
        
        # Calculate profit
        profit = total_result_value - total_cost
        profit_margin = (profit / total_cost * 100) if total_cost > 0 else 0
        
        return {
            'cost': total_cost,
            'result_value': total_result_value,
            'profit': profit,
            'profit_margin': profit_margin,
            'roi': (profit / total_cost * 100) if total_cost > 0 else 0,
            'material_costs': cost_data['material_costs']
        }
    
    @staticmethod
    def filter_recipes(recipes: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter recipes based on criteria."""
        filtered_recipes = recipes
        
        # Filter by profession
        if 'profession' in filters and filters['profession']:
            profession = filters['profession'].lower()
            filtered_recipes = [
                r for r in filtered_recipes 
                if r.get('profession', '').lower() == profession
            ]
        
        # Filter by skill level
        if 'min_skill' in filters and filters['min_skill'] is not None:
            min_skill = int(filters['min_skill'])
            filtered_recipes = [
                r for r in filtered_recipes 
                if r.get('skill_level', 0) >= min_skill
            ]
        
        if 'max_skill' in filters and filters['max_skill'] is not None:
            max_skill = int(filters['max_skill'])
            filtered_recipes = [
                r for r in filtered_recipes 
                if r.get('skill_level', 0) <= max_skill
            ]
        
        # Filter by profitability
        if 'min_profit' in filters and filters['min_profit'] is not None:
            min_profit = float(filters['min_profit'])
            materials_data = DataLoader.load_materials_data()
            filtered_recipes = [
                r for r in filtered_recipes
                if DataProcessor.calculate_recipe_profit(r, materials_data)['profit'] >= min_profit
            ]
        
        # Filter by search term
        if 'search' in filters and filters['search']:
            search_term = filters['search'].lower()
            filtered_recipes = [
                r for r in filtered_recipes
                if search_term in r.get('name', '').lower()
            ]
        
        return filtered_recipes
    
    @staticmethod
    def sort_recipes(recipes: List[Dict[str, Any]], sort_by: str = 'name', 
                    sort_order: str = 'asc') -> List[Dict[str, Any]]:
        """Sort recipes by specified criteria."""
        reverse = sort_order.lower() == 'desc'
        
        if sort_by == 'profit':
            materials_data = DataLoader.load_materials_data()
            recipes_with_profit = []
            for recipe in recipes:
                profit_data = DataProcessor.calculate_recipe_profit(recipe, materials_data)
                recipes_with_profit.append((recipe, profit_data['profit']))
            
            recipes_with_profit.sort(key=lambda x: x[1], reverse=reverse)
            return [r[0] for r in recipes_with_profit]
        
        elif sort_by == 'skill_level':
            return sorted(recipes, key=lambda x: x.get('skill_level', 0), reverse=reverse)
        
        elif sort_by == 'name':
            return sorted(recipes, key=lambda x: x.get('name', ''), reverse=reverse)
        
        elif sort_by == 'profession':
            return sorted(recipes, key=lambda x: x.get('profession', ''), reverse=reverse)
        
        return recipes


class DataLoader:
    """Loads and manages data files."""
    
    @staticmethod
    def load_recipes_data() -> List[Dict[str, Any]]:
        """Load recipes data from file."""
        try:
            if not RECIPES_FILE.exists():
                logger.warning(f"Recipes file not found: {RECIPES_FILE}")
                return []
            
            with open(RECIPES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different data formats
            if isinstance(data, dict) and 'recipes' in data:
                recipes = data['recipes']
            elif isinstance(data, list):
                recipes = data
            else:
                logger.error("Invalid recipes data format")
                return []
            
            # Validate recipes
            valid_recipes = []
            for recipe in recipes:
                if DataValidator.validate_recipe(recipe):
                    valid_recipes.append(recipe)
                else:
                    logger.warning(f"Skipping invalid recipe: {recipe.get('name', 'Unknown')}")
            
            logger.info(f"Loaded {len(valid_recipes)} valid recipes")
            return valid_recipes
            
        except Exception as e:
            logger.error(f"Error loading recipes data: {e}")
            return []
    
    @staticmethod
    def load_materials_data() -> Dict[str, Any]:
        """Load materials data from file."""
        try:
            if not MATERIALS_FILE.exists():
                logger.warning(f"Materials file not found: {MATERIALS_FILE}")
                return {}
            
            with open(MATERIALS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not DataValidator.validate_materials_data(data):
                logger.error("Invalid materials data format")
                return {}
            
            logger.info(f"Loaded {len(data)} materials")
            return data
            
        except Exception as e:
            logger.error(f"Error loading materials data: {e}")
            return {}
    
    @staticmethod
    def save_recipes_data(recipes: List[Dict[str, Any]], backup: bool = True) -> bool:
        """Save recipes data to file."""
        try:
            if backup and DATA_CONFIG['backup_enabled']:
                DataLoader._backup_file(RECIPES_FILE)
            
            # Create backup of current data
            output_data = {
                'recipes': recipes,
                'metadata': {
                    'total_recipes': len(recipes),
                    'exported_at': datetime.now().isoformat(),
                    'version': '1.0'
                }
            }
            
            with open(RECIPES_FILE, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(recipes)} recipes to {RECIPES_FILE}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving recipes data: {e}")
            return False
    
    @staticmethod
    def save_materials_data(materials: Dict[str, Any], backup: bool = True) -> bool:
        """Save materials data to file."""
        try:
            if backup and DATA_CONFIG['backup_enabled']:
                DataLoader._backup_file(MATERIALS_FILE)
            
            with open(MATERIALS_FILE, 'w', encoding='utf-8') as f:
                json.dump(materials, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(materials)} materials to {MATERIALS_FILE}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving materials data: {e}")
            return False
    
    @staticmethod
    def _backup_file(file_path: Path) -> None:
        """Create a backup of a file."""
        if not file_path.exists():
            return
        
        backup_dir = file_path.parent / 'backups'
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = backup_dir / backup_name
        
        import shutil
        shutil.copy2(file_path, backup_path)
        
        # Clean up old backups
        DataLoader._cleanup_backups(backup_dir, file_path.stem)
    
    @staticmethod
    def _cleanup_backups(backup_dir: Path, file_stem: str) -> None:
        """Clean up old backup files."""
        backup_count = DATA_CONFIG.get('backup_count', 5)
        
        backup_files = sorted([
            f for f in backup_dir.glob(f"{file_stem}_*")
            if f.is_file()
        ])
        
        # Remove old backups
        if len(backup_files) > backup_count:
            for old_backup in backup_files[:-backup_count]:
                old_backup.unlink()
                logger.debug(f"Removed old backup: {old_backup}")


class URLProcessor:
    """Processes and validates URLs."""
    
    @staticmethod
    def validate_wowhead_url(url: str) -> bool:
        """Validate if URL is a valid Wowhead recipe URL."""
        try:
            parsed = urlparse(url)
            if parsed.netloc != 'www.wowhead.com':
                return False
            
            # Check if it's a spell/recipe URL
            spell_pattern = r'/classic/spell=\d+'
            return bool(re.search(spell_pattern, parsed.path))
            
        except Exception:
            return False
    
    @staticmethod
    def extract_recipe_id(url: str) -> Optional[int]:
        """Extract recipe ID from Wowhead URL."""
        try:
            match = re.search(r'spell=(\d+)', url)
            return int(match.group(1)) if match else None
        except Exception:
            return None
    
    @staticmethod
    def clean_urls(urls: List[str]) -> List[str]:
        """Clean and validate a list of URLs."""
        cleaned_urls = []
        
        for url in urls:
            url = url.strip()
            if not url or url.startswith('#'):
                continue
            
            if URLProcessor.validate_wowhead_url(url):
                cleaned_urls.append(url)
            else:
                logger.warning(f"Invalid URL skipped: {url}")
        
        return cleaned_urls


class PriceCalculator:
    """Calculates prices and profits."""
    
    @staticmethod
    def format_price(price: float) -> str:
        """Format price as gold, silver, copper."""
        if price < 0:
            return f"-{PriceCalculator.format_price(abs(price))}"
        
        gold = int(price // 10000)
        silver = int((price % 10000) // 100)
        copper = int(price % 100)
        
        if gold > 0:
            return f"{gold}g {silver}s {copper}c"
        elif silver > 0:
            return f"{silver}s {copper}c"
        else:
            return f"{copper}c"
    
    @staticmethod
    def parse_price(price_str: str) -> float:
        """Parse price string to copper value."""
        total_copper = 0
        
        # Extract gold
        gold_match = re.search(r'(\d+)g', price_str)
        if gold_match:
            total_copper += int(gold_match.group(1)) * 10000
        
        # Extract silver
        silver_match = re.search(r'(\d+)s', price_str)
        if silver_match:
            total_copper += int(silver_match.group(1)) * 100
        
        # Extract copper
        copper_match = re.search(r'(\d+)c', price_str)
        if copper_match:
            total_copper += int(copper_match.group(1))
        
        return float(total_copper)
    
    @staticmethod
    def calculate_ah_fees(sell_price: float, deposit: float = 0) -> Dict[str, float]:
        """Calculate Auction House fees."""
        # 5% cut for successful sales
        ah_cut = sell_price * 0.05
        listing_fee = deposit
        
        return {
            'ah_cut': ah_cut,
            'listing_fee': listing_fee,
            'total_fees': ah_cut + listing_fee,
            'net_profit': sell_price - ah_cut - listing_fee
        }


# Export main classes and functions
__all__ = [
    'DataValidator',
    'DataProcessor', 
    'DataLoader',
    'URLProcessor',
    'PriceCalculator'
]