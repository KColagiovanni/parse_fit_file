# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import json
# from bs4 import BeautifulSoup
# import time
# import re
# import requests
# import config
#
#
# def get_strength_details(activity_id):
#
#     activity_url = f'https://connect.garmin.com/modern/activity/{activity_id}'
#     time.sleep(3)
#
#     driver = webdriver.Chrome()
#     driver.get(activity_url)
#
#     print(driver.page_source[:4000])
#
#     # Wait for the table to load
#     table = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located(
#             (
#                 # By.TAG_NAME,
#                 # "table"
#                 By.CSS_SELECTOR,
#                 'table'
#             )
#         )
#     )
#
#     rows = table.find_elements(By.TAG_NAME, "tr")
#     for row in rows:
#         cols = row.find_elements(By.TAG_NAME, "td")
#
#         # Process the data in each column
#         cell_texts = [c.text.strip() for c in cols]
#         print(cell_texts)
#
#     driver.quit()
#
# def login_to_garmin_connect():
#     # the URL of the login page
#     login_url = "https://connect.garmin.com/signin"
#
#     # the payload with your login credentials
#     payload = config.login_credentials
#
#     # send the POST request to login
#     response = requests.post(login_url, data=payload)
#
#     # if the request went Ok, you should get a 200 status
#     print(f"Status code: {response.status_code}")
#
#     # parse the HTML content using BeautifulSoup
#     soup = BeautifulSoup(response.text, "html.parser")
#
#     # find the page title
#     page_title = soup.title.string
#
#     # print the result page title
#     print(f"Page title: {page_title}")
#
# if '__main__' == __name__:
#
#     login_to_garmin_connect()
#     get_strength_details('21091110845')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

def scrape_strength(activity_id):
    url = f"https://connect.garmin.com/modern/activity/{activity_id}"

    driver = webdriver.Chrome()
    driver.get(url)

    wait = WebDriverWait(driver, 20)

    # The rep-counting table Garmin uses
    TABLE_SELECTOR = "#repCountingActivityViewPlaceholder table"

    print("⏳ Waiting for strength table...")

    table = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, TABLE_SELECTOR))
    )

    print("✅ Strength table found.")

    rows = table.find_elements(By.TAG_NAME, "tr")

    parsed = []
    for row in rows:
        cols = [c.text.strip() for c in row.find_elements(By.TAG_NAME, "td")]
        if any(cols):  # skip empty rows
            parsed.append(cols)
            print(cols)

    driver.quit()
    return parsed


if __name__ == "__main__":
    activity_id = "21091110845"

    while True:
        try:
            scrape_strength(activity_id)
        except StaleElementReferenceException:
            continue
        else:
            break