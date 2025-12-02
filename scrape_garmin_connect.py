from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from bs4 import BeautifulSoup
import time
import re
import requests
import config


def get_strength_details(activity_id):

    # document.querySelector("#repCountingActivityViewPlaceholder > div > div:nth-child(2) > table")

    activity_url = f'https://connect.garmin.com/modern/activity/{activity_id}'
    time.sleep(3)

    # options = Options()
    # options.add_argument("--headless")  # run in background
    # options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    #                      "AppleWebKit/537.36 (KHTML, like Gecko) "
    #                      "Chrome/120.0.0.0 Safari/537.36")
    # driver = webdriver.Chrome(options=options)
    driver = webdriver.Chrome()
    driver.get(activity_url)

    print(driver.page_source[:4000])

    # Wait for the table to load
    table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                # By.TAG_NAME,
                # "table"
                By.CSS_SELECTOR,
                'table'
            )
        )
    )

    rows = table.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        # Process the data in each column
        # print(f'cols is: {cols}')
        cell_texts = [c.text.strip() for c in cols]
        print(cell_texts)

    driver.quit()

    # response = requests.get(activity_url)
    # response.raise_for_status()
    # soup = BeautifulSoup(response.text, 'html.parser')
    # # html_content = response.content
    # # soup = BeautifulSoup(html_content, 'html.parser')
    #
    # # json_script = soup.find('script', {'id': 'ld_searchpage_results', 'type': 'application/ld+json'})
    # table = soup.find('table')
    # rows = table.find_all('tr')
    #
    # for row in rows:
    #     cols = row.find_all('td')
    #     print(f'Cols is: {cols}')

def login_to_garmin_connect():
    # the URL of the login page
    login_url = "https://connect.garmin.com/signin"

    # the payload with your login credentials
    payload = config.login_credentials

    # send the POST request to login
    response = requests.post(login_url, data=payload)

    # if the request went Ok, you should get a 200 status
    print(f"Status code: {response.status_code}")

    # parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # find the page title
    page_title = soup.title.string

    # print the result page title
    print(f"Page title: {page_title}")

if '__main__' == __name__:

    login_to_garmin_connect()
    get_strength_details('21091110845')