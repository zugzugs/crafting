# scrape_wowhead.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def scroll_to_bottom(driver, pause_time=2):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)

        # Calculate new scroll height and compare with last
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # We're at the bottom
        last_height = new_height

def main():
    url = "https://www.wowhead.com/items"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    scroll_to_bottom(driver, pause_time=10)

    time.sleep(10)

    items = driver.find_elements(By.CSS_SELECTOR, ".listview-mode-default a.listview-cleartext")
    for item in items:
        print(item.text)

    driver.quit()

if __name__ == "__main__":
    main()
