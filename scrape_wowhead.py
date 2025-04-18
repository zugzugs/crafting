from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json
import re
import time

def get_materials_data(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(2)  # Let the JS load a bit

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract recipeId from URL
    recipe_id_match = re.search(r"spell=(\d+)", url)
    recipe_id = int(recipe_id_match.group(1)) if recipe_id_match else 0

    # Extract recipe name
    name_tag = soup.find("h1", class_="heading-size-1")
    name = name_tag.text.strip() if name_tag else "Unknown"

    # Extract materials
    materials = []
    materials_section = soup.find("div", class_="reagent-list")
    if materials_section:
        for reagent in materials_section.select(".reagent"):
            item_link = reagent.select_one("a[href*='item=']")
            if item_link:
                item_id_match = re.search(r"item=(\d+)", item_link["href"])
                item_id = int(item_id_match.group(1)) if item_id_match else 0
                quantity_text = reagent.get_text(strip=True)
                quantity_match = re.search(r"x(\d+)", quantity_text)
                quantity = int(quantity_match.group(1)) if quantity_match else 1

                materials.append({
                    "itemId": item_id,
                    "quantity": quantity
                })

    # Default values for profession and skillLevel
    profession = "Unknown"
    skill_level = 0

    # Assume the result item is the recipe itself (you can modify if needed)
    result = {
        "itemId": recipe_id,
        "quantity": 1
    }

    # Final JSON structure
    recipe_data = {
        "recipeId": recipe_id,
        "name": name,
        "profession": profession,
        "skillLevel": skill_level,
        "result": result,
        "materials": materials
    }

    driver.quit()
    return recipe_data

# Example usage
if __name__ == "__main__":
    url = "https://www.wowhead.com/classic/spell=1225763/grand-lobster-banquet"
    recipe_json = get_materials_data(url)
    print(json.dumps([recipe_json], indent=4))
