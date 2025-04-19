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
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Recipe ID from URL
    recipe_id_match = re.search(r"spell=(\d+)", url)
    recipe_id = int(recipe_id_match.group(1)) if recipe_id_match else 0

    # Recipe name
    name_tag = soup.find("h1", class_="heading-size-1")
    name = name_tag.text.strip() if name_tag else "Unknown"

    # Recipe icon
    icon_name = ""
    icon_li = soup.select_one("li.icon-db-link ins[style]")
    if icon_li and "background-image" in icon_li["style"]:
        match = re.search(r'url\(["\']?(.*?)["\']?\)', icon_li["style"])
        if match:
            icon_url = match.group(1)
            icon_name = icon_url.split('/')[-1].split('.')[0]



    # Profession from breadcrumb (last <a> in breadcrumb)
    breadcrumb = soup.select_one("div.breadcrumb")
    profession = "Unknown"
    if breadcrumb:
        links = breadcrumb.find_all("a")
        if links:
            profession = links[-1].text.strip()

    # Reagents
    reagents_div = soup.select_one("div.indent.q1")
    materials = []
    if reagents_div:
        reagent_text = reagents_div.get_text(separator=' ', strip=True)
        links = reagents_div.find_all("a")

        for link in links:
            href = link.get("href", "")
            item_id_match = re.search(r"item=(\d+)", href)
            if item_id_match:
                item_id = int(item_id_match.group(1))
                material_name = link.text.strip()  # <- fixed here

                quantity_match = re.search(re.escape(material_name) + r"\s*\((\d+)\)", reagent_text)
                quantity = int(quantity_match.group(1)) if quantity_match else 1

                materials.append({
                    "itemId": item_id,
                    "quantity": quantity
                })


    # Result item ID
    result_item = soup.select_one("span.q2 a[href*='/item=']")
    result_item_id = 0
    if result_item:
        item_id_match = re.search(r"item=(\d+)", result_item["href"])
        if item_id_match:
            result_item_id = int(item_id_match.group(1))

    # Quantity crafted (default 1 if unknown)
    quantity_match = re.search(r"\((\d+)\)", result_item.text if result_item else "")
    result_quantity = int(quantity_match.group(1)) if quantity_match else 1

    result = {
        "itemId": result_item_id or recipe_id,
        "quantity": result_quantity
    }

    # Final structure
    recipe_data = {
        "recipeId": recipe_id,
        "name": name,
        "profession": profession,
        "skillLevel": 0,
        "icon": icon_name,
        "result": result,
        "materials": materials
    }


    driver.quit()
    return recipe_data

def scrape_from_file(input_file, output_file):
    with open(input_file, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    all_recipes = []
    for url in urls:
        try:
            print(f"Scraping: {url}")
            recipe = get_materials_data(url)
            all_recipes.append(recipe)
        except Exception as e:
            print(f"Error scraping {url}: {e}")

    with open(output_file, "w") as f:
        json.dump(all_recipes, f, indent=4)

    print(f"\nSaved {len(all_recipes)} recipes to {output_file}")


if __name__ == "__main__":
    scrape_from_file("urls.txt", "recipes.json")
    recipe_json = get_materials_data(url)
    print(json.dumps([recipe_json], indent=4))
