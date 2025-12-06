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

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX Working Code XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import StaleElementReferenceException
#
# def scrape_strength(activity_id):
#     url = f"https://connect.garmin.com/modern/activity/{activity_id}"
#
#     driver = webdriver.Chrome()
#     driver.get(url)
#
#     wait = WebDriverWait(driver, 20)
#
#     # The rep-counting table Garmin uses
#     TABLE_SELECTOR = "#repCountingActivityViewPlaceholder table"
#
#     print("⏳ Waiting for strength table...")
#
#     table = wait.until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, TABLE_SELECTOR))
#     )
#
#     print("✅ Strength table found.")
#
#     rows = table.find_elements(By.TAG_NAME, "tr")
#
#     parsed = []
#     for row in rows:
#         cols = [c.text.strip() for c in row.find_elements(By.TAG_NAME, "td")]
#         if any(cols):  # skip empty rows
#             parsed.append(cols)
#             print(cols)
#
#     driver.quit()
#     return parsed
#
#
# if __name__ == "__main__":
#     activity_id = "21091110845"
#
#     while True:
#         try:
#             scrape_strength(activity_id)
#         except StaleElementReferenceException:
#             continue
#         else:
#             break
#
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

import csv
import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ----------------------------------
#   SCRAPE A SINGLE STRENGTH ACTIVITY
# ----------------------------------

def scrape_strength_activity(activity_id):
    url = f"https://connect.garmin.com/modern/activity/{activity_id}"

    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=opts)
    driver.get(url)

    # Wait for table
    try:
        table = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#repCountingActivityViewPlaceholder table")
            )
        )
    except Exception:
        driver.quit()
        raise RuntimeError("❌ No strength table found — Is this a strength workout?")

    rows = table.find_elements(By.TAG_NAME, "tr")

    # -------------------------------------
    # Robust Header Extraction
    # -------------------------------------
    header_elems = rows[0].find_elements(By.TAG_NAME, "th")
    headers = [h.text.strip() for h in header_elems if h.text.strip()]

    print("DEBUG headers:", headers)

    # If header row is empty → use fallback headers
    if not headers:
        headers = ["Set", "Exercise Name", "Time", "Rest", "Reps", "Weight", "Volume"]
        print("⚠️ WARNING: No headers found. Using fallback:", headers)

    # -------------------------------------
    # Parse Data Rows (with mismatch handling)
    # -------------------------------------
    sets = []
    for r in rows[1:]:
        cols = [c.text.strip() for c in r.find_elements(By.TAG_NAME, "td")]
        print("cols is:", cols)

        if not cols:
            continue

        # If Garmin outputs more columns or fewer columns than headers, fix it
        if len(cols) != len(headers):
            print(f"⚠️ MISMATCH: {len(headers)} headers vs {len(cols)} cols")
            print("Skipping this row:", cols)
            continue

        rowdict = dict(zip(headers, cols))
        sets.append(rowdict)

    print("\nsets is:", sets)

    driver.quit()
    return sets


# ----------------------------------
#   SAVE TO CSV
# ----------------------------------

def save_csv(activity_id, sets):
    filename = f"garmin_strength_{activity_id}.csv"

    if not sets:
        print("❌ No data to save.")
        return

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(sets[0].keys()))
        writer.writeheader()
        writer.writerows(sets)

    print(f"💾 CSV saved → {filename}")


# ----------------------------------
#   SAVE TO SQLITE
# ----------------------------------

def save_sqlite(activity_id, sets):
    conn = sqlite3.connect("garmin_strength.db")
    cur = conn.cursor()

    # Create table if needed
    cur.execute("""
        CREATE TABLE IF NOT EXISTS strength_sets (
            activity_id TEXT,
            set_number INTEGER,
            exercise TEXT,
            time TEXT,
            rest TEXT,
            reps INTEGER,
            weight TEXT,
            volume TEXT
        )
    """)

    # Insert set data
    for s in sets:
        cur.execute("""
            INSERT INTO strength_sets 
            (activity_id, set_number, exercise, time, rest, reps, weight, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            activity_id,
            s.get("Set"),
            s.get("Exercise Name"),
            s.get("Time"),
            s.get("Rest"),
            s.get("Reps"),
            s.get("Weight"),
            s.get("Volume")
        ))

    conn.commit()
    conn.close()
    print("💾 SQLite updated → garmin_strength.db")


# ----------------------------------
#   MAIN
# ----------------------------------

if __name__ == "__main__":
    # activity_id = input("Enter Garmin Strength Activity ID: ").strip()
    activity_id = "21091110845"

    print(f"🔎 Scraping strength workout {activity_id}...")
    sets = scrape_strength_activity(activity_id)

    print(f"✅ Extracted {len(sets)} sets.")
    for s in sets[:3]:
        print("   ", s)

    save_csv(activity_id, sets)
    save_sqlite(activity_id, sets)

    print("\n🎉 DONE!")
