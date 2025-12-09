from strength_training import StrengthTraining
from selenium.common.exceptions import StaleElementReferenceException

st = StrengthTraining()

if __name__ == "__main__":
    # activity_id = input("Enter Garmin Strength Activity ID: ").strip()
    activity_id = '21091110845'

    print(f'Scraping strength workout {activity_id}...')
    while True:
        try:
            sets = st.scrape_strength_activity(activity_id)
            # scrape_strength(activity_id)
        except StaleElementReferenceException:
            continue
        else:
            break

    print(f'Extracted {len(sets)} sets.')
    for s in sets[:3]:
        print(f'   {s}')

    st.save_csv(activity_id, sets)
    st.save_sqlite(activity_id, sets)

    print('\nDone!')
