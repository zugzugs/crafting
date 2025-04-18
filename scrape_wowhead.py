# scrape_wowhead.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def main():
    url = "https://www.wowhead.com/items"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    time.sleep(10)

    items = driver.find_elements(By.CSS_SELECTOR, ".listview-mode-default a.listview-cleartext")
    for item in items:
        print(item.text)

    driver.quit()

if __name__ == "__main__":
    main()
