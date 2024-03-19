from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import json

# Setup Selenium WebDriver
driver = webdriver.Chrome()  # Update the path to your ChromeDriver

# Load URLs from a JSON file
with open('recipe_links.json', 'r') as file:
    urls = json.load(file)["recipe_links"]

all_recipes_data = []
count = 0
for url in urls:
    count += 1
    driver.get(url)
    print(url)

    # Allow some time for the page to load
    time.sleep(5)

    # Extracting the recipe title
    title = driver.find_element(By.TAG_NAME, 'h1').text

    # Extracting the ingredients
    ingredients_list = driver.find_elements(By.XPATH, '//h2[contains(text(), "Ingredients")]/following-sibling::ul/li')
    ingredients = [ingredient.text for ingredient in ingredients_list]

    # Extracting the preparation steps
    preparation_steps_list = driver.find_elements(By.CSS_SELECTOR, ".instructions__steps__step")
    preparation_steps = []
    for step in preparation_steps_list:
        step_title = step.find_element(By.CSS_SELECTOR, ".instructions__steps__step--title").text
        step_body = step.find_element(By.CSS_SELECTOR, ".instructions__steps__step--body").text
        preparation_steps.append(f"{step_title} {step_body}")

    if len(preparation_steps) > 0:
        preparation_steps.pop()

    # Extracting the recipe details
    recipe_details_elements = driver.find_elements(By.CSS_SELECTOR, ".header__details__items__list")
    recipe_details = {detail.text.split(": ")[0]: detail.text.split(": ")[1] for detail in recipe_details_elements}

    parsed_ingredients = []

    for ingredient in ingredients:
        parts = ingredient.split("\n")
        name = parts[-1].strip()  # The name is assumed to be after the last newline
        # Remove mL content and extract amount and measurement
        amount_measurement = parts[0].split("(")[0].strip()
        amount, measurement = amount_measurement.split(" ", 1) if " " in amount_measurement else (amount_measurement, "")

        parsed_ingredients.append({
            "name": name,
            "measurement": measurement,
            "amount": amount
        })

    ingredients = parsed_ingredients


    nutrition_button = driver.find_element(By.CSS_SELECTOR, ".nutrition__header")
    nutrition_button.click()

    # # Allow some time for the page to load
    # time.sleep(2)


    nutrition_info = {}
    try:
        # Try to find the nutritional information
        nutrition_info = {
            'Sodium': driver.find_element(By.XPATH, "//p[text()='Sodium']/parent::*/following-sibling::div/p").text,
            'Protein': driver.find_element(By.XPATH, "//p[text()='Protein']/parent::*/following-sibling::div/p").text,
            'Calories': driver.find_element(By.XPATH, "//p[text()='Calories']/parent::*/following-sibling::div/p").text,
            'Total Fat': driver.find_element(By.XPATH, "//p[text()='Total Fat']/parent::*/following-sibling::div/p").text,
            # For Sugars and Dietary Fibre, if they are not structured with a following div containing the value, 
            # you may need to adjust the strategy to find these elements.
        }
    
        # Iterate through the original dictionary and split each value
        nutrition_info_split = {}
        for key, value in nutrition_info.items():
            if ' ' in value:
                amount, unit = value.split(' ', 1)  # Splits into amount and unit based on the first space
            else:
                amount = value  # The entire value is treated as the amount
                unit = ""  # Unit is set to an empty string
            nutrition_info_split[key] = {'amount': amount, 'unit': unit}

        nutritional_info = nutrition_info_split

    except NoSuchElementException:
    # If no nutritional information found, stop the loop
        pass

    recipe_data = {
        "title": title,
        "ingredients": ingredients,
        "preparation_steps": preparation_steps,
        "details": recipe_details,
        "nutritional_info": nutritional_info
    }

    all_recipes_data.append(recipe_data)

    if count % 10 == 0:
        # Specify the filename
        filename = 'remaining_recipes_data.json'

        # Writing the data to a JSON file
        with open(filename, 'w') as file:
            json.dump(all_recipes_data, file, indent=4)


# Specify the filename
filename = 'remaining_recipes_data.json'

# Writing the data to a JSON file
with open(filename, 'w') as file:
    json.dump(all_recipes_data, file, indent=4)

# Closing the WebDriver
driver.quit()
