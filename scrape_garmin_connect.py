import csv
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException


# Scrape a single strength activity.
def scrape_strength_activity(activity_id):
    url = f"https://connect.garmin.com/modern/activity/{activity_id}"

    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=opts)
    driver.get(url)

    # Wait for table.
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

    # Robust Header Extraction.
    header_elems = rows[0].find_elements(By.TAG_NAME, "th")
    headers = [h.text.strip() for h in header_elems if h.text.strip()]

    print("DEBUG headers:", headers)

    # If header row is empty, use fallback headers.
    if not headers:
        headers = ["Set", "Exercise Name", "Time", "Rest", "Reps", "Weight", "Volume"]
        print("WARNING: No headers found. Using fallback:", headers)

    # Parse Data Rows (with mismatch handling).
    sets = []
    for r in rows[1:]:
        cols = [c.text.strip() for c in r.find_elements(By.TAG_NAME, "td")]

        if not cols:
            continue

        # If Garmin outputs more columns or fewer columns than headers, fix it.
        if len(cols) != len(headers):
            print(f"MISMATCH: {len(headers)} headers vs {len(cols)} cols")
            print("Skipping this row:", cols)
            continue

        rowdict = dict(zip(headers, cols))
        sets.append(rowdict)

    driver.quit()
    return sets


# Save to CSV.
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


# Save to SQLite.
def save_sqlite(activity_id, sets):
    conn = sqlite3.connect("garmin_strength.db")
    cur = conn.cursor()

    # Create table if needed.
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
    print(f"SQLite updated. Save as: garmin_strength.db")


# Main
if __name__ == "__main__":
    # activity_id = input("Enter Garmin Strength Activity ID: ").strip()
    activity_id = "21091110845"

    print(f"Scraping strength workout {activity_id}...")
    while True:
        try:
            sets = scrape_strength_activity(activity_id)
            # scrape_strength(activity_id)
        except StaleElementReferenceException:
            continue
        else:
            break

    print(f"Extracted {len(sets)} sets.")
    for s in sets[:3]:
        print("   ", s)

    save_csv(activity_id, sets)
    save_sqlite(activity_id, sets)

    print("\nDone!")
