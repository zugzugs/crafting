#!/usr/bin/env python3
"""
Simple Flask web server for WoW Classic SoD Recipe Calculator
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from config import WEB_CONFIG, PROJECT_ROOT
from utils import DataLoader, DataProcessor, DataValidator, PriceCalculator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global data cache
recipes_cache = []
materials_cache = {}


def load_data():
    """Load data into cache."""
    global recipes_cache, materials_cache
    
    try:
        recipes_cache = DataLoader.load_recipes_data()
        materials_cache = DataLoader.load_materials_data()
        logger.info(f"Loaded {len(recipes_cache)} recipes and {len(materials_cache)} materials")
    except Exception as e:
        logger.error(f"Error loading data: {e}")


@app.route('/')
def index():
    """Serve the main HTML file."""
    return send_from_directory(PROJECT_ROOT, 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory(PROJECT_ROOT, filename)


@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    """Get all recipes with optional filtering."""
    try:
        # Get query parameters
        profession = request.args.get('profession')
        min_skill = request.args.get('min_skill', type=int)
        max_skill = request.args.get('max_skill', type=int)
        search = request.args.get('search')
        min_profit = request.args.get('min_profit', type=float)
        sort_by = request.args.get('sort_by', 'name')
        sort_order = request.args.get('sort_order', 'asc')
        
        # Build filters
        filters = {}
        if profession:
            filters['profession'] = profession
        if min_skill is not None:
            filters['min_skill'] = min_skill
        if max_skill is not None:
            filters['max_skill'] = max_skill
        if search:
            filters['search'] = search
        if min_profit is not None:
            filters['min_profit'] = min_profit
        
        # Filter and sort recipes
        filtered_recipes = DataProcessor.filter_recipes(recipes_cache, filters)
        sorted_recipes = DataProcessor.sort_recipes(filtered_recipes, sort_by, sort_order)
        
        # Calculate profits for each recipe
        recipes_with_profit = []
        for recipe in sorted_recipes:
            profit_data = DataProcessor.calculate_recipe_profit(recipe, materials_cache)
            recipe_with_profit = recipe.copy()
            recipe_with_profit['profit_data'] = profit_data
            recipes_with_profit.append(recipe_with_profit)
        
        return jsonify({
            'success': True,
            'data': recipes_with_profit,
            'total': len(recipes_with_profit),
            'filters': filters
        })
        
    except Exception as e:
        logger.error(f"Error getting recipes: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """Get a specific recipe by ID."""
    try:
        recipe = next((r for r in recipes_cache if r['recipe_id'] == recipe_id), None)
        
        if not recipe:
            return jsonify({
                'success': False,
                'error': 'Recipe not found'
            }), 404
        
        # Calculate profit data
        profit_data = DataProcessor.calculate_recipe_profit(recipe, materials_cache)
        recipe_with_profit = recipe.copy()
        recipe_with_profit['profit_data'] = profit_data
        
        return jsonify({
            'success': True,
            'data': recipe_with_profit
        })
        
    except Exception as e:
        logger.error(f"Error getting recipe {recipe_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/materials', methods=['GET'])
def get_materials():
    """Get all materials."""
    try:
        return jsonify({
            'success': True,
            'data': materials_cache,
            'total': len(materials_cache)
        })
        
    except Exception as e:
        logger.error(f"Error getting materials: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/materials/<item_id>', methods=['GET'])
def get_material(item_id):
    """Get a specific material by ID."""
    try:
        material = materials_cache.get(str(item_id))
        
        if not material:
            return jsonify({
                'success': False,
                'error': 'Material not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': material
        })
        
    except Exception as e:
        logger.error(f"Error getting material {item_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/professions', methods=['GET'])
def get_professions():
    """Get all professions."""
    try:
        from config import PROFESSIONS
        return jsonify({
            'success': True,
            'data': PROFESSIONS
        })
        
    except Exception as e:
        logger.error(f"Error getting professions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/calculate-profit', methods=['POST'])
def calculate_profit():
    """Calculate profit for a recipe with custom prices."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        recipe_id = data.get('recipe_id')
        result_price = data.get('result_price', 0)
        material_prices = data.get('material_prices', {})
        
        # Find recipe
        recipe = next((r for r in recipes_cache if r['recipe_id'] == recipe_id), None)
        if not recipe:
            return jsonify({
                'success': False,
                'error': 'Recipe not found'
            }), 404
        
        # Create custom materials data with provided prices
        custom_materials = materials_cache.copy()
        for item_id, price in material_prices.items():
            if str(item_id) in custom_materials:
                custom_materials[str(item_id)]['price'] = price
        
        # Calculate profit
        profit_data = DataProcessor.calculate_recipe_profit(recipe, custom_materials, result_price)
        
        return jsonify({
            'success': True,
            'data': {
                'recipe': recipe,
                'profit_data': profit_data,
                'custom_prices': material_prices
            }
        })
        
    except Exception as e:
        logger.error(f"Error calculating profit: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get application statistics."""
    try:
        # Calculate basic stats
        total_recipes = len(recipes_cache)
        total_materials = len(materials_cache)
        
        # Profession breakdown
        profession_stats = {}
        for recipe in recipes_cache:
            profession = recipe.get('profession', 'Unknown')
            profession_stats[profession] = profession_stats.get(profession, 0) + 1
        
        # Profitability stats
        profitable_recipes = 0
        total_profit = 0
        for recipe in recipes_cache:
            profit_data = DataProcessor.calculate_recipe_profit(recipe, materials_cache)
            if profit_data['profit'] > 0:
                profitable_recipes += 1
                total_profit += profit_data['profit']
        
        avg_profit = total_profit / profitable_recipes if profitable_recipes > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_recipes': total_recipes,
                'total_materials': total_materials,
                'profession_breakdown': profession_stats,
                'profitable_recipes': profitable_recipes,
                'profitability_rate': (profitable_recipes / total_recipes * 100) if total_recipes > 0 else 0,
                'average_profit': avg_profit,
                'total_profit': total_profit
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'recipes_loaded': len(recipes_cache),
        'materials_loaded': len(materials_cache)
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


def main():
    """Main function to run the server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="WoW Classic SoD Recipe Calculator Server")
    parser.add_argument("--host", default=WEB_CONFIG['host'], 
                       help="Host to bind to")
    parser.add_argument("--port", type=int, default=WEB_CONFIG['port'], 
                       help="Port to bind to")
    parser.add_argument("--debug", action="store_true", 
                       help="Enable debug mode")
    parser.add_argument("--reload", action="store_true", 
                       help="Enable auto-reload")
    
    args = parser.parse_args()
    
    # Load data
    logger.info("Loading data...")
    load_data()
    
    # Run server
    logger.info(f"Starting server on {args.host}:{args.port}")
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        use_reloader=args.reload
    )


if __name__ == "__main__":
    main()