from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
from config import EMAIL, PASSW

# Credentials


# Website URL
LOGIN_URL = 'https://ankiweb.net/account/login'
DECK_NAME = 'Google_translator_06_23'  # Adjust this if needed

# Initialize Chrome WebDriver
options = webdriver.ChromeOptions()
service = Service()
driver = webdriver.Chrome(service=service, options=options)


def login():
    """Logs into AnkiWeb."""
    driver.get(LOGIN_URL)

    # Enter email
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Email']"))
    ).send_keys(EMAIL)

    # Enter password
    driver.find_element(By.XPATH, "//input[@placeholder='Password']").send_keys(PASSW)

    # Click login button
    driver.find_element(By.XPATH, "//button[@class='btn btn-primary btn-lg']").click()

    time.sleep(3)  # Wait for login


def open_deck():
    """Opens the specified Anki deck."""
    try:
        deck = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[15]/div[1]/button'))
        )
        deck.click()
    except Exception as e:
        print(f"Error opening deck: {e}")
        driver.quit()
        exit()


def press_button(button_text):
    """Presses 'Hard' or 'Easy' buttons."""
    try:
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{button_text}')]"))
        )
        button.click()
    except Exception as e:
        print(f"Error clicking '{button_text}': {e}")


def extract_word():
    """Extracts the word from the edit page."""
    try:
        # Open edit page in a new tab
        driver.find_element(By.XPATH, '//div[@id="quiz"]/div[1]/a[1]').click()
        driver.switch_to.window(driver.window_handles[1])  # Switch to new tab

        # Get word
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div/main//div[1]/div/div"))
        )
        words = element.text.strip().split("\n")
        second_word = words[-1]  # Last word in the list

        driver.close()  # Close tab
        driver.switch_to.window(driver.window_handles[0])  # Switch back

        return second_word
    except Exception as e:
        print(f"Error extracting word: {e}")
        return None


def process_cards():
    """Main loop to process Anki cards."""
    words_list = []

    while True:
        try:
            # Click "Show Answer"
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@id="ansarea"]/div/div/button'))
            ).click()

            word = extract_word()
            if word:
                if word not in words_list:
                    words_list.append(word)
                    press_button("Hard")
                else:
                    press_button("Easy")

            time.sleep(2)  # Wait for next card

        except Exception as e:
            print(f"Error processing card: {e}")
            break

    return words_list


def save_to_csv(words):
    """Saves words to a CSV file."""
    with open('mojalista.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Words"])  # Header
        writer.writerows([[word] for word in words])

    print("Exported words to 'my_words.csv'.")


# Execute script
login()
open_deck()
word_list = process_cards()
save_to_csv(word_list)

driver.quit()
