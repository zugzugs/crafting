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
    driver.set_page_load_timeout(15)
    driver.set_script_timeout(15)

    driver.get(url)
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")

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
            icon_name = icon_url.split("/")[-1].split(".")[0]

    # Profession from breadcrumb
    breadcrumb = soup.select_one("div.breadcrumb")
    profession = "Unknown"
    if breadcrumb:
        links = breadcrumb.find_all("a")
        if links:
            profession = links[-1].text.strip()

    # Reagents (robust approach to avoid Tools mix-up)
    materials = []
    td = soup.find("td")

    if td:
        reagents_label = td.find(string=re.compile(r"Reagents:"))
        if reagents_label:
            # Get the next sibling div after "Reagents:"
            reagents_div = reagents_label.find_next("div", class_="indent q1")
            if reagents_div:
                reagent_text = reagents_div.get_text(separator=" ", strip=True)
                links = reagents_div.find_all("a")
                for link in links:
                    href = link.get("href", "")
                    item_id_match = re.search(r"item=(\d+)", href)
                    if item_id_match:
                        item_id = int(item_id_match.group(1))
                        material_name = link.text.strip()

                        quantity_match = re.search(
                            re.escape(material_name) + r"\s*\((\d+)\)", reagent_text
                        )
                        quantity = int(quantity_match.group(1)) if quantity_match else 1

                        materials.append({"itemId": item_id, "quantity": quantity})

    # Result itemId and quantity from tooltip
    result_item_id = 0
    result_quantity = 1
    tooltip_div = soup.select_one(f"div#tt{recipe_id}")
    if tooltip_div:
        # Get itemId from link in tooltip
        item_links = tooltip_div.select("a[href*='/item=']")
        item_link = item_links[-1] if item_links else None
        print(item_link)
        if item_link:
            item_id_match = re.search(r"item=(\d+)", item_link["href"])
            print(item_id_match)
            if item_id_match:
                result_item_id = int(item_id_match.group(1))
                print(result_item_id)

        # Get quantity from tooltip text
        tooltip_text = tooltip_div.get_text(separator=" ", strip=True)
        match = re.search(re.escape(name) + r"\s*\(\s*(\d+)\s*\)", tooltip_text)
        if match:
            result_quantity = int(match.group(1))

    # Fallback: ensure result_item_id never equals recipeId
    if result_item_id == recipe_id:
        result_item_id = 0

    result = {"itemId": result_item_id, "quantity": result_quantity}

    recipe_data = {
        "recipeId": recipe_id,
        "name": name,
        "profession": profession,
        "skillLevel": 0,
        "icon": icon_name,
        "result": result,
        "materials": materials,
    }

    driver.quit()
    return recipe_data


def scrape_from_file(input_file, output_file, max_retries=3, delay=2):
    with open(input_file, "r") as f:
        urls = [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        ]

    all_recipes = []
    failed_urls = []

    def try_scrape(url):
        for attempt in range(1, max_retries + 1):
            try:
                print(f"Scraping (Attempt {attempt}): {url}")
                recipe = get_materials_data(url)
                all_recipes.append(recipe)
                return True
            except Exception as e:
                print(f"Error on attempt {attempt} for {url}: {e}")
                time.sleep(delay)  # wait before retry
        return False

    for url in urls:
        success = try_scrape(url)
        if not success:
            failed_urls.append(url)

    # Write successful recipes
    with open(output_file, "w") as f:
        json.dump(all_recipes, f, indent=4)

    # Optionally save the failed ones
    if failed_urls:
        with open("failed_urls.txt", "w") as f:
            f.write("\n".join(failed_urls))
        print(
            f"\n⚠️ Failed to scrape {len(failed_urls)} recipes. Saved to failed_urls.txt"
        )

    print(f"\n✅ Successfully saved {len(all_recipes)} recipes to {output_file}")


if __name__ == "__main__":
    scrape_from_file("urls.txt", "recipes.json")
