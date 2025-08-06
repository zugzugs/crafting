#!/usr/bin/env python3
"""
Test suite for WoW Classic SoD Recipe Calculator
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from config import PROFESSIONS, DEFAULT_VENDOR_PRICES
from utils import (
    DataValidator, DataProcessor, DataLoader, 
    URLProcessor, PriceCalculator
)


class TestDataValidator(unittest.TestCase):
    """Test data validation functions."""
    
    def setUp(self):
        self.valid_recipe = {
            "recipe_id": 12345,
            "name": "Test Recipe",
            "profession": "Cooking",
            "skill_level": 285,
            "icon_name": "inv_misc_food_01",
            "materials": [
                {"itemId": 123, "quantity": 2},
                {"itemId": 456, "quantity": 1}
            ],
            "result_item_id": 789,
            "result_quantity": 1,
            "url": "https://www.wowhead.com/classic/spell=12345",
            "scraped_at": "2024-01-15 10:30:00"
        }
        
        self.valid_material = {
            "itemId": 123,
            "quantity": 2
        }
        
        self.valid_materials_data = {
            "123": {
                "name": "Test Material",
                "price": 100,
                "vendor_price": 50,
                "icon": "inv_misc_food_01"
            }
        }
    
    def test_validate_recipe_valid(self):
        """Test validation of valid recipe."""
        self.assertTrue(DataValidator.validate_recipe(self.valid_recipe))
    
    def test_validate_recipe_missing_field(self):
        """Test validation of recipe with missing field."""
        invalid_recipe = self.valid_recipe.copy()
        del invalid_recipe["name"]
        self.assertFalse(DataValidator.validate_recipe(invalid_recipe))
    
    def test_validate_recipe_invalid_type(self):
        """Test validation of recipe with invalid type."""
        invalid_recipe = self.valid_recipe.copy()
        invalid_recipe["recipe_id"] = "not_an_integer"
        self.assertFalse(DataValidator.validate_recipe(invalid_recipe))
    
    def test_validate_material_valid(self):
        """Test validation of valid material."""
        self.assertTrue(DataValidator.validate_material(self.valid_material))
    
    def test_validate_material_invalid_quantity(self):
        """Test validation of material with invalid quantity."""
        invalid_material = self.valid_material.copy()
        invalid_material["quantity"] = 0
        self.assertFalse(DataValidator.validate_material(invalid_material))
    
    def test_validate_materials_data_valid(self):
        """Test validation of valid materials data."""
        self.assertTrue(DataValidator.validate_materials_data(self.valid_materials_data))
    
    def test_validate_materials_data_invalid_structure(self):
        """Test validation of materials data with invalid structure."""
        invalid_data = {
            "123": "not_a_dict"
        }
        self.assertFalse(DataValidator.validate_materials_data(invalid_data))


class TestDataProcessor(unittest.TestCase):
    """Test data processing functions."""
    
    def setUp(self):
        self.test_recipe = {
            "recipe_id": 12345,
            "name": "Test Recipe",
            "profession": "Cooking",
            "skill_level": 285,
            "materials": [
                {"itemId": 123, "quantity": 2},
                {"itemId": 456, "quantity": 1}
            ],
            "result_item_id": 789,
            "result_quantity": 1
        }
        
        self.test_materials_data = {
            "123": {
                "name": "Material 1",
                "price": 100
            },
            "456": {
                "name": "Material 2", 
                "price": 50
            }
        }
    
    def test_calculate_recipe_cost(self):
        """Test recipe cost calculation."""
        cost_data = DataProcessor.calculate_recipe_cost(self.test_recipe, self.test_materials_data)
        
        expected_cost = 2 * 100 + 1 * 50  # 250
        self.assertEqual(cost_data["total_cost"], expected_cost)
        self.assertEqual(len(cost_data["material_costs"]), 2)
    
    def test_calculate_recipe_cost_with_vendor_fallback(self):
        """Test recipe cost calculation with vendor price fallback."""
        materials_data = {"123": {"name": "Material 1", "price": 100}}
        cost_data = DataProcessor.calculate_recipe_cost(self.test_recipe, materials_data)
        
        # Material 456 should use vendor price (2 copper)
        expected_cost = 2 * 100 + 1 * 2  # 202
        self.assertEqual(cost_data["total_cost"], expected_cost)
    
    def test_calculate_recipe_profit(self):
        """Test recipe profit calculation."""
        result_price = 500
        profit_data = DataProcessor.calculate_recipe_profit(
            self.test_recipe, self.test_materials_data, result_price
        )
        
        expected_cost = 2 * 100 + 1 * 50  # 250
        expected_profit = 500 - expected_cost  # 250
        expected_margin = (250 / 250) * 100  # 100%
        
        self.assertEqual(profit_data["cost"], expected_cost)
        self.assertEqual(profit_data["result_value"], result_price)
        self.assertEqual(profit_data["profit"], expected_profit)
        self.assertEqual(profit_data["profit_margin"], expected_margin)
    
    def test_filter_recipes_by_profession(self):
        """Test recipe filtering by profession."""
        recipes = [
            {"name": "Recipe 1", "profession": "Cooking"},
            {"name": "Recipe 2", "profession": "Alchemy"},
            {"name": "Recipe 3", "profession": "Cooking"}
        ]
        
        filtered = DataProcessor.filter_recipes(recipes, {"profession": "Cooking"})
        self.assertEqual(len(filtered), 2)
        self.assertTrue(all(r["profession"] == "Cooking" for r in filtered))
    
    def test_filter_recipes_by_skill_level(self):
        """Test recipe filtering by skill level."""
        recipes = [
            {"name": "Recipe 1", "skill_level": 100},
            {"name": "Recipe 2", "skill_level": 200},
            {"name": "Recipe 3", "skill_level": 300}
        ]
        
        filtered = DataProcessor.filter_recipes(recipes, {"min_skill": 200})
        self.assertEqual(len(filtered), 2)
        self.assertTrue(all(r["skill_level"] >= 200 for r in filtered))
    
    def test_sort_recipes_by_name(self):
        """Test recipe sorting by name."""
        recipes = [
            {"name": "Zebra Recipe"},
            {"name": "Apple Recipe"},
            {"name": "Banana Recipe"}
        ]
        
        sorted_recipes = DataProcessor.sort_recipes(recipes, "name", "asc")
        self.assertEqual(sorted_recipes[0]["name"], "Apple Recipe")
        self.assertEqual(sorted_recipes[-1]["name"], "Zebra Recipe")


class TestURLProcessor(unittest.TestCase):
    """Test URL processing functions."""
    
    def test_validate_wowhead_url_valid(self):
        """Test validation of valid Wowhead URL."""
        valid_url = "https://www.wowhead.com/classic/spell=12345/test-recipe"
        self.assertTrue(URLProcessor.validate_wowhead_url(valid_url))
    
    def test_validate_wowhead_url_invalid_domain(self):
        """Test validation of URL with invalid domain."""
        invalid_url = "https://example.com/classic/spell=12345/test-recipe"
        self.assertFalse(URLProcessor.validate_wowhead_url(invalid_url))
    
    def test_validate_wowhead_url_invalid_path(self):
        """Test validation of URL with invalid path."""
        invalid_url = "https://www.wowhead.com/item=12345/test-item"
        self.assertFalse(URLProcessor.validate_wowhead_url(invalid_url))
    
    def test_extract_recipe_id(self):
        """Test recipe ID extraction."""
        url = "https://www.wowhead.com/classic/spell=12345/test-recipe"
        recipe_id = URLProcessor.extract_recipe_id(url)
        self.assertEqual(recipe_id, 12345)
    
    def test_extract_recipe_id_invalid(self):
        """Test recipe ID extraction from invalid URL."""
        url = "https://www.wowhead.com/item=12345/test-item"
        recipe_id = URLProcessor.extract_recipe_id(url)
        self.assertIsNone(recipe_id)
    
    def test_clean_urls(self):
        """Test URL cleaning and validation."""
        urls = [
            "https://www.wowhead.com/classic/spell=12345/recipe-1",
            "# Comment line",
            "https://www.wowhead.com/classic/spell=67890/recipe-2",
            "https://example.com/invalid-url",
            "  https://www.wowhead.com/classic/spell=11111/recipe-3  "
        ]
        
        cleaned = URLProcessor.clean_urls(urls)
        self.assertEqual(len(cleaned), 3)
        self.assertTrue(all(URLProcessor.validate_wowhead_url(url) for url in cleaned))


class TestPriceCalculator(unittest.TestCase):
    """Test price calculation functions."""
    
    def test_format_price_gold(self):
        """Test price formatting with gold."""
        price = 12345  # 1g 23s 45c
        formatted = PriceCalculator.format_price(price)
        self.assertEqual(formatted, "1g 23s 45c")
    
    def test_format_price_silver(self):
        """Test price formatting with silver only."""
        price = 1234  # 12s 34c
        formatted = PriceCalculator.format_price(price)
        self.assertEqual(formatted, "12s 34c")
    
    def test_format_price_copper(self):
        """Test price formatting with copper only."""
        price = 99  # 99c
        formatted = PriceCalculator.format_price(price)
        self.assertEqual(formatted, "99c")
    
    def test_format_price_negative(self):
        """Test price formatting with negative value."""
        price = -12345
        formatted = PriceCalculator.format_price(price)
        self.assertEqual(formatted, "-1g 23s 45c")
    
    def test_parse_price_gold(self):
        """Test price parsing with gold."""
        price_str = "1g 23s 45c"
        parsed = PriceCalculator.parse_price(price_str)
        self.assertEqual(parsed, 12345)
    
    def test_parse_price_silver(self):
        """Test price parsing with silver only."""
        price_str = "12s 34c"
        parsed = PriceCalculator.parse_price(price_str)
        self.assertEqual(parsed, 1234)
    
    def test_parse_price_copper(self):
        """Test price parsing with copper only."""
        price_str = "99c"
        parsed = PriceCalculator.parse_price(price_str)
        self.assertEqual(parsed, 99)
    
    def test_calculate_ah_fees(self):
        """Test Auction House fee calculation."""
        sell_price = 1000
        fees = PriceCalculator.calculate_ah_fees(sell_price, deposit=50)
        
        self.assertEqual(fees["ah_cut"], 50)  # 5% of 1000
        self.assertEqual(fees["listing_fee"], 50)
        self.assertEqual(fees["total_fees"], 100)
        self.assertEqual(fees["net_profit"], 900)


class TestDataLoader(unittest.TestCase):
    """Test data loading functions."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_recipes_data_valid(self):
        """Test loading valid recipes data."""
        test_data = {
            "recipes": [
                {
                    "recipe_id": 12345,
                    "name": "Test Recipe",
                    "profession": "Cooking",
                    "skill_level": 285,
                    "materials": [{"itemId": 123, "quantity": 1}],
                    "result_item_id": 789,
                    "result_quantity": 1
                }
            ]
        }
        
        recipes_file = self.temp_path / "recipes.json"
        with open(recipes_file, 'w') as f:
            json.dump(test_data, f)
        
        with patch('utils.RECIPES_FILE', recipes_file):
            recipes = DataLoader.load_recipes_data()
            self.assertEqual(len(recipes), 1)
            self.assertEqual(recipes[0]["name"], "Test Recipe")
    
    def test_load_recipes_data_invalid_format(self):
        """Test loading recipes data with invalid format."""
        test_data = "invalid json"
        recipes_file = self.temp_path / "recipes.json"
        with open(recipes_file, 'w') as f:
            f.write(test_data)
        
        with patch('utils.RECIPES_FILE', recipes_file):
            recipes = DataLoader.load_recipes_data()
            self.assertEqual(len(recipes), 0)
    
    def test_load_materials_data_valid(self):
        """Test loading valid materials data."""
        test_data = {
            "123": {
                "name": "Test Material",
                "price": 100
            }
        }
        
        materials_file = self.temp_path / "materials.json"
        with open(materials_file, 'w') as f:
            json.dump(test_data, f)
        
        with patch('utils.MATERIALS_FILE', materials_file):
            materials = DataLoader.load_materials_data()
            self.assertEqual(len(materials), 1)
            self.assertEqual(materials["123"]["name"], "Test Material")
    
    def test_load_materials_data_file_not_found(self):
        """Test loading materials data when file doesn't exist."""
        materials_file = self.temp_path / "nonexistent.json"
        
        with patch('utils.MATERIALS_FILE', materials_file):
            materials = DataLoader.load_materials_data()
            self.assertEqual(materials, {})


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow."""
    
    def test_complete_workflow(self):
        """Test complete workflow from data loading to profit calculation."""
        # Test data
        recipe = {
            "recipe_id": 12345,
            "name": "Test Recipe",
            "profession": "Cooking",
            "skill_level": 285,
            "materials": [
                {"itemId": 123, "quantity": 2},
                {"itemId": 456, "quantity": 1}
            ],
            "result_item_id": 789,
            "result_quantity": 1
        }
        
        materials_data = {
            "123": {"name": "Material 1", "price": 100},
            "456": {"name": "Material 2", "price": 50}
        }
        
        # Validate recipe
        self.assertTrue(DataValidator.validate_recipe(recipe))
        
        # Calculate cost
        cost_data = DataProcessor.calculate_recipe_cost(recipe, materials_data)
        self.assertEqual(cost_data["total_cost"], 250)
        
        # Calculate profit
        profit_data = DataProcessor.calculate_recipe_profit(recipe, materials_data, 500)
        self.assertEqual(profit_data["profit"], 250)
        self.assertEqual(profit_data["profit_margin"], 100.0)
        
        # Format price
        formatted_profit = PriceCalculator.format_price(profit_data["profit"])
        self.assertEqual(formatted_profit, "2s 50c")


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)