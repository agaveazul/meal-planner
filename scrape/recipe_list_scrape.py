from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import json


# URL of the recipe
url = "https://www.presidentschoice.ca/recipes"

# Setup Selenium WebDriver
driver = webdriver.Chrome()  # Update the path to your ChromeDriver
driver.get(url)



for _ in range(100):
    # Scroll to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    try:
        # Try to find the button and click it
        button = driver.find_element(By.CLASS_NAME, 'recipe-tabs__show-more__button')
        button.click()
    except NoSuchElementException:
        # If button is not found, stop the loop
        break
    
    # Pause for 0.5 seconds
    time.sleep(0.5)


# Find all anchor tags within the list items of the recipes list
recipe_links = driver.find_elements(By.CSS_SELECTOR, "#ecommerce_listview_recipestab1 .recipe-tile__img-container")

# Extract the href attributes
hrefs = [link.get_attribute('href') for link in recipe_links]

# Define the JSON structure
data = {
    "recipe_links": hrefs
}

# Specify the JSON file name
filename = 'recipes_links.json'

# Write the data to a JSON file
with open(filename, 'w') as file:
    json.dump(data, file, indent=4)

print(f"Data stored in {filename}")

# Close the driver when done
driver.quit()

