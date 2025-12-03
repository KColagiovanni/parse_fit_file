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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import requests
import json
import config

LOGIN_URL = "https://connect.garmin.com/signin/?next=%2Fmodern%2F"
DETAILS_URL = "https://connect.garmin.com/modern/proxy/activity-service/activity/{id}/details"


def selenium_login():
    print("🌐 Launching browser...")

    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    driver.get(LOGIN_URL)

    # Wait for page JS to load
    time.sleep(5)

    print("🔐 Waiting for login fields...")

    # USERNAME
    user_box = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="username"]'))
    )
    user_box.send_keys(config.GARMIN_USERNAME)
    time.sleep(1)

    # PASSWORD
    pass_box = driver.find_element(By.CSS_SELECTOR, 'input[name="password"]')
    pass_box.send_keys(config.GARMIN_PASSWORD)
    time.sleep(1)

    # SUBMIT button
    login_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    login_btn.click()

    print("⏳ Logging in... waiting for redirect to account...")
    time.sleep(10)

    # Check that login succeeded
    if "signin" in driver.current_url:
        print("❌ Login failed — still on signin page")
    else:
        print(f"✅ Login successful → {driver.current_url}")

    cookies = driver.get_cookies()
    driver.quit()
    return cookies


def cookies_to_requests_session(cookies):
    session = requests.Session()
    for c in cookies:
        session.cookies.set(c['name'], c['value'])
    return session


def fetch_strength_details(activity_id):
    print("🔎 Logging into Garmin...")
    cookies = selenium_login()
    session = cookies_to_requests_session(cookies)

    url = DETAILS_URL.format(id=activity_id)
    print(f"📡 Requesting: {url}")

    r = session.get(url)
    print(f"Status: {r.status_code}")

    try:
        data = r.json()
    except:
        print("❌ Failed to parse JSON")
        print(r.text[:600])
        return

    if "sets" not in data:
        print("❌ No strength data returned. Activity private or session invalid.")
        print(json.dumps(data, indent=2))
        return

    sets = data["sets"]

    print(f"💪 Found {len(sets)} sets:\n")

    for s in sets:
        print(
            f"{s.get('exerciseName','N/A'):25} | "
            f"Reps {s.get('reps')} | "
            f"Weight {s.get('weight')} | "
            f"Volume {s.get('volume')}"
        )


if __name__ == "__main__":
    activity_id = input("Enter Garmin activity ID: ")
    fetch_strength_details(activity_id)
