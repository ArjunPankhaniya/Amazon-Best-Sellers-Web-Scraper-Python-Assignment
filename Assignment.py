from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import csv
import json

# Constants
BEST_SELLER_URL = "https://www.amazon.in/gp/bestsellers/?ref_=nav_em_cs_bestsellers_0_1_1_2"
CATEGORY_URLS = [
    "https://www.amazon.in/gp/bestsellers/kitchen/ref=zg_bs_nav_kitchen_0",
    "https://www.amazon.in/gp/bestsellers/shoes/ref=zg_bs_nav_shoes_0",
    "https://www.amazon.in/gp/bestsellers/computers/ref=zg_bs_nav_computers_0",
    "https://www.amazon.in/gp/bestsellers/electronics/ref=zg_bs_nav_electronics_0",
    # Add more category URLs as needed
]
MAX_PRODUCTS = 1500
DISCOUNT_THRESHOLD = 50

# Initialize WebDriver
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)
    return driver

# Login to Amazon
def login_amazon(driver, username, password):
    driver.get("https://www.amazon.in/ap/signin")
    try:
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_email"))
        )
        email_field.send_keys(username)
        email_field.send_keys(Keys.RETURN)

        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_password"))
        )
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
    except TimeoutException:
        print("Login failed: Timeout while waiting for input fields.")

# Scrape category data
def scrape_category(driver, category_url):
    driver.get(category_url)
    products = []

    while len(products) < MAX_PRODUCTS:
        try:
            items = driver.find_elements(By.CSS_SELECTOR, '.zg-item-immersion')
            for item in items:
                try:
                    product_name = item.find_element(By.CSS_SELECTOR, ".p13n-sc-truncated").text
                    product_price = item.find_element(By.CSS_SELECTOR, ".p13n-sc-price").text
                    discount = None  # Implement discount extraction logic if available
                    rating = item.find_element(By.CSS_SELECTOR, ".a-icon-alt").get_attribute("innerHTML")
                    ship_from = None  # Placeholder, implement extraction logic
                    sold_by = None  # Placeholder, implement extraction logic
                    description = None  # Placeholder, implement extraction logic
                    num_bought = None  # Placeholder, implement extraction logic
                    category_name = category_url.split('/')[-2]

                    # Collect images
                    images = [img.get_attribute('src') for img in item.find_elements(By.CSS_SELECTOR, "img")]

                    if discount is not None and int(discount.strip('%')) > DISCOUNT_THRESHOLD:
                        products.append({
                            "Product Name": product_name,
                            "Product Price": product_price,
                            "Sale Discount": discount,
                            "Best Seller Rating": rating,
                            "Ship From": ship_from,
                            "Sold By": sold_by,
                            "Rating": rating,
                            "Product Description": description,
                            "Number Bought in the Past Month": num_bought,
                            "Category Name": category_name,
                            "Images": images
                        })

                except NoSuchElementException:
                    continue

            next_button = driver.find_elements(By.CSS_SELECTOR, ".a-pagination .a-last a")
            if next_button:
                next_button[0].click()
                time.sleep(2)
            else:
                break

        except Exception as e:
            print(f"Error while scraping category: {e}")
            break

    return products

# Save data to file
def save_data(data, filename, file_format="csv"):
    if data:
        if file_format == "csv":
            keys = data[0].keys()
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
        elif file_format == "json":
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

# Main function
def main():
    username = "your_email@example.com"
    password = "your_password"

    driver = init_driver()
    login_amazon(driver, username, password)

    all_products = []
    for category_url in CATEGORY_URLS:
        products = scrape_category(driver, category_url)
        all_products.extend(products)

    if all_products:
        save_data(all_products, "amazon_best_sellers.csv", "csv")
    driver.quit()

if __name__ == "__main__":
    main()
