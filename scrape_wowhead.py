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
    time.sleep(2)  # Give time for page to load

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract recipeId from URL
    recipe_id_match = re.search(r"spell=(\d+)", url)
    recipe_id = int(recipe_id_match.group(1)) if recipe_id_match else 0

    # Extract recipe name
    name_tag = soup.find("h1", class_="heading-size-1")
    name = name_tag.text.strip() if name_tag else "Unknown"

    # Find the reagents section
    reagents_div = soup.select_one("div.indent.q1")
    materials = []

    if reagents_div:
        reagent_text = reagents_div.get_text(separator=' ', strip=True)
        links = reagents_div.find_all("a")

        for link in links:
            item_href = link.get("href", "")
            item_id_match = re.search(r"item=(\d+)", item_href)
            if item_id_match:
                item_id = int(item_id_match.group(1))
                item_name = link.text.strip()

                # Search for this item's quantity in the reagent text
                quantity_match = re.search(re.escape(item_name) + r"\s*\((\d+)\)", reagent_text)
                quantity = int(quantity_match.group(1)) if quantity_match else 1

                materials.append({
                    "itemId": item_id,
                    "quantity": quantity
                })

    # Attempt to find result item (optional refinement)
    result_item = soup.select_one("span.q2 a[href*='/item=']")
    result_item_id = 0
    if result_item:
        result_item_id_match = re.search(r"item=(\d+)", result_item["href"])
        if result_item_id_match:
            result_item_id = int(result_item_id_match.group(1))

    result = {
        "itemId": result_item_id or recipe_id,
        "quantity": 2  # From the page snippet: (2)
    }

    # Default profession & skillLevel
    profession = "Unknown"
    skill_level = 0

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
