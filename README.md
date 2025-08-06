# WoW Classic SoD Recipe Profit Calculator

A comprehensive tool for analyzing World of Warcraft Classic Season of Discovery recipe profitability. This project scrapes recipe data from Wowhead and provides a web interface for profit calculations.

## Features

- **Automated Recipe Scraping**: Scrapes recipe data from Wowhead with robust error handling
- **Profit Calculation**: Real-time profit analysis with material costs and vendor prices
- **Modern Web Interface**: Responsive design with dark/light mode support
- **Advanced Filtering**: Filter by profession, skill level, and profitability
- **Data Export**: Export results to JSON format
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## Project Structure

```
├── scrape_wowhead.py      # Main scraper script
├── index.html             # Web interface
├── indexv2.html          # Enhanced web interface
├── cooking.html          # Cooking-specific interface
├── requirements.txt      # Python dependencies
├── recipes.json          # Scraped recipe data
├── materials.json        # Material price data
├── urls.txt             # URLs to scrape
└── README.md            # This file
```

## Installation

### Prerequisites

- Python 3.8+
- Google Chrome browser
- ChromeDriver (automatically managed by Selenium)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd wow-classic-sod-calculator
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install ChromeDriver** (if not already installed):
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install chromium-chromedriver
   
   # On macOS with Homebrew
   brew install chromedriver
   
   # On Windows, download from https://chromedriver.chromium.org/
   ```

## Usage

### Scraping Recipes

1. **Prepare URLs**: Create a text file with Wowhead recipe URLs (one per line):
   ```
   https://www.wowhead.com/classic/spell=12345/recipe-name
   https://www.wowhead.com/classic/spell=67890/another-recipe
   ```

2. **Run the scraper**:
   ```bash
   python scrape_wowhead.py urls.txt recipes.json
   ```

3. **Advanced scraping options**:
   ```bash
   python scrape_wowhead.py urls.txt recipes.json \
     --headless \
     --timeout 20 \
     --max-retries 5 \
     --delay 3.0
   ```

### Web Interface

1. **Start a local server**:
   ```bash
   # Using Python's built-in server
   python -m http.server 8000
   
   # Or using Node.js
   npx serve .
   ```

2. **Open in browser**: Navigate to `http://localhost:8000`

3. **Load data**: The interface will automatically load `recipes.json` and `materials.json`

## Configuration

### Scraper Settings

The scraper supports various configuration options:

- `--headless`: Run browser in headless mode (default: True)
- `--timeout`: Page load timeout in seconds (default: 15)
- `--max-retries`: Maximum retry attempts per URL (default: 3)
- `--delay`: Delay between requests in seconds (default: 2.0)

### Data Format

#### Recipe Data Structure
```json
{
  "recipe_id": 12345,
  "name": "Recipe Name",
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
```

#### Materials Data Structure
```json
{
  "itemId": {
    "name": "Item Name",
    "price": 100,
    "vendor_price": 50,
    "icon": "inv_misc_food_01"
  }
}
```

## Features in Detail

### Profit Calculation
- **Material Costs**: Calculated from current market prices
- **Vendor Prices**: Default prices for vendor-sold items
- **Crafting Costs**: Includes skill level requirements
- **Profit Margin**: Real-time profit/loss calculation

### Advanced Filtering
- **Profession Filter**: Filter by specific professions
- **Skill Level**: Filter by required skill level
- **Profitability**: Show only profitable recipes
- **Search**: Text search across recipe names

### Data Management
- **Automatic Updates**: Scrape fresh data from Wowhead
- **Backup System**: Automatic backup of existing data
- **Error Recovery**: Robust error handling and retry logic
- **Logging**: Comprehensive logging for debugging

## Development

### Code Quality

The project uses several tools for code quality:

```bash
# Format code
black scrape_wowhead.py

# Lint code
flake8 scrape_wowhead.py

# Type checking
mypy scrape_wowhead.py

# Run tests
pytest
```

### Adding New Features

1. **New Data Fields**: Update the `RecipeData` dataclass
2. **New Filters**: Add filter logic to the web interface
3. **New Calculations**: Extend the profit calculation logic

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**:
   ```bash
   # Install ChromeDriver
   pip install webdriver-manager
   ```

2. **Scraping fails**:
   - Check internet connection
   - Verify URLs are valid
   - Check Wowhead's robots.txt
   - Increase delay between requests

3. **Web interface not loading**:
   - Ensure files are in the correct location
   - Check browser console for errors
   - Verify JSON files are valid

### Logs

Check the `scraper.log` file for detailed error information:

```bash
tail -f scraper.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Wowhead](https://www.wowhead.com/) for providing recipe data
- [Bootstrap](https://getbootstrap.com/) for the UI framework
- [Selenium](https://selenium.dev/) for web scraping capabilities

## Roadmap

- [ ] Async scraping for better performance
- [ ] Database integration for persistent storage
- [ ] API endpoints for external integrations
- [ ] Mobile app version
- [ ] Real-time price updates
- [ ] Advanced analytics and reporting
