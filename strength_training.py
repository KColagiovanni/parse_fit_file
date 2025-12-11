import csv
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class StrengthTraining:

    def __init__(self):
        self.DATABASE_NAME = 'garmin_strength.db'

    # Scrape a single strength activity.
    def scrape_strength_activity(self, activity_id):
        url = f'https://connect.garmin.com/modern/activity/{activity_id}'

        opts = Options()
        opts.add_argument('--headless=new')
        opts.add_argument('--disable-blink-features=AutomationControlled')
        opts.add_argument('--window-size=1920,1080')

        driver = webdriver.Chrome(options=opts)
        driver.get(url)

        # Wait for table.
        try:
            table = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '#repCountingActivityViewPlaceholder table')
                )
            )
        except Exception:
            driver.quit()
            raise RuntimeError('No strength table found — Is this a strength workout?')

        rows = table.find_elements(By.TAG_NAME, 'tr')

        # Robust Header Extraction.
        header_elems = rows[0].find_elements(By.TAG_NAME, 'th')
        headers = [h.text.strip() for h in header_elems if h.text.strip()]

        # If header row is empty, use fallback headers.
        if not headers:
            headers = ['Set', 'Exercise Name', 'Time', 'Rest', 'Reps', 'Weight', 'Volume']
            print(f'WARNING: No headers found. Using fallback: {headers}')

        # Parse Data Rows (with mismatch handling).
        sets = []
        for r in rows[1:]:
            cols = [c.text.strip() for c in r.find_elements(By.TAG_NAME, 'td')]

            if not cols:
                continue

            # If Garmin outputs more columns or fewer columns than headers, fix it.
            if len(cols) != len(headers):
                print(f'MISMATCH: {len(headers)} headers vs {len(cols)} cols')
                print(f'Skipping this row: {cols}')
                continue

            rowdict = dict(zip(headers, cols))
            sets.append(rowdict)

        driver.quit()
        return sets

    # Save to CSV.
    @staticmethod
    def save_csv(activity_id, sets):
        filename = f'garmin_strength_{activity_id}.csv'

        if not sets:
            print('No data to save.')
            return

        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(sets[0].keys()))
            writer.writeheader()
            writer.writerows(sets)

        print(f'CSV saved → {filename}')

    # Save to SQLite.
    def save_sqlite(self, activity_id, sets):
        conn = sqlite3.connect(self.DATABASE_NAME)
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

        # One row per Garmin activity.
        cur.execute("""
            CREATE TABLE workouts (
                workout_id TEXT PRIMARY KEY,    -- Garmin activity ID
                date TEXT,
                start_time TEXT,
                duration_seconds INTEGER,
                total_volume REAL,
                total_sets INTEGER,
                total_reps INTEGER
            )
        """)

        # Unique exercise names with an ID.
        cur.execute("""
            CREATE TABLE exercises (
                exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
        """)

        # Every set performed in every workout (THOUSANDS of rows).
        cur.execute("""
            CREATE TABLE sets (
                set_id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_id TEXT,
                set_number INTEGER,
                exercise_id INTEGER,
                duration_seconds REAL,
                rest_seconds REAL,
                reps INTEGER,
                weight REAL,
                volume REAL,
                FOREIGN KEY(workout_id) REFERENCES workouts(workout_id),
                FOREIGN KEY(exercise_id) REFERENCES exercises(exercise_id)
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
                s.get('Set'),
                s.get('Exercise Name'),
                s.get('Time'),
                s.get('Rest'),
                s.get('Reps'),
                s.get('Weight'),
                s.get('Volume')
            ))

        conn.commit()
        conn.close()
        print(f'SQLite updated. Save as: {self.DATABASE_NAME}')