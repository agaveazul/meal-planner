from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import json

def save_file():
    # Specify the filename
    filename = 'product_catalogue.json'

    # Writing the data to a JSON file
    with open(filename, 'w') as file:
        json.dump(product_catalogue, file, indent=4)

def split_at_first_letter(s):
    # Find the index of the first letter
    for i, char in enumerate(s):
        if char.isalpha():
            # Split the string into number and letter portions
            number_part = s[:i]
            letter_part = s[i:]
            return number_part, letter_part

def extract_price_amount_unit(data):
    if ", " in data:
        parts = data.split(", ")
        if " " in parts[1]:
            sub_parts = parts[1].split()
            price, quantity = sub_parts[1].split("/")
            amount, unit = split_at_first_letter(quantity)    
        else:
            price, quantity = parts[1].split("/")
            amount, unit = split_at_first_letter(quantity)
    elif " " in data:
        parts = data.split()
        if "/" not in parts[1]:
            price = ""
            amount = ""
            unit = ""
        else:
            price, quantity = parts[1].split("/")
            amount, unit = split_at_first_letter(quantity)
    elif " " not in data: 
        price, quantity = data.split("/")
        amount, unit = split_at_first_letter(quantity)
    else:
        price = ""
        amount = ""
        unit = ""
    return price, amount, unit

product_catalogue = []

# Setup WebDriver
driver = webdriver.Chrome()
n = 209
base_url = "https://www.realcanadiansuperstore.ca/food/c/27985"

for i in range(n):
    url = base_url + "?page=" + str(i+1)
    driver.get(url)

    # Allow some time for the page to load
    if i == 0:
        time.sleep(10)
    else:
        time.sleep(3)

    # Locate all product elements by class name
    product_elements = driver.find_elements(By.CSS_SELECTOR, '.chakra-linkbox.css-vhnn8v')

    for product in product_elements:
        # Extract the product name, price, and quantity within each product element
        name = product.find_element(By.CSS_SELECTOR, 'h3[data-testid="product-title"]').text
        brand = ""
        try: 
            brand = product.find_element(By.CSS_SELECTOR, 'p[data-testid="product-brand"]').text
        except NoSuchElementException:
            # If no nutritional information found, stop the loop
            pass
        if len(brand) > 0:
            name = brand + " " + name
        price_quantity = product.find_element(By.CSS_SELECTOR, 'p[data-testid="product-package-size"]').text
        price, quantity, unit = extract_price_amount_unit(price_quantity)

        product = {"name": name, "price": price, "quantity": quantity, "unit": unit}
        product_catalogue.append(product)
    

save_file()

# Close the WebDriver
driver.quit()