# promo_tester.py

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def wait_for_spinner_to_disappear(driver, timeout=10):
    try:
        WebDriverWait(driver, timeout).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='general__Loading']"))
        )
    except:
        print("Spinner did not disappear in time.")

# Read words
with open("unique_words.txt", "r", encoding="utf-8") as f:
    unique_words = [line.strip() for line in f if line.strip()]

# Generate promo codes
promo_codes = []
for word in unique_words:
    # for i in range(45, 0, -5):
    for i in [30]:
        promo_codes.append(f"{word}{i}")
# print(promo_codes)

# Setup Headless Chrome
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--log-level=3")
options.add_argument("--disable-logging")
options.add_experimental_option("excludeSwitches", ["enable-logging"])

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Load checkout page
checkout_url = "https://www.rbo.org.uk/checkout/interstitial/66245"
driver.get(checkout_url)
time.sleep(3)

try:
    accept_btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'accept')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", accept_btn)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", accept_btn)
    # print("Accepted cookie banner (checkout).")
    time.sleep(1)
except Exception:
    # print("ℹNo visible cookie banner on checkout page.")
    pass

wait = WebDriverWait(driver, 10)
successful_codes = []

for code in promo_codes:
    try:
        input_box = wait.until(EC.presence_of_element_located((By.NAME, "promo-code-input")))
        driver.execute_script("arguments[0].scrollIntoView(true);", input_box)
        input_box.clear()
        input_box.send_keys(code)

        apply_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(text(), 'Apply promotional code')]")
        ))
        driver.execute_script("arguments[0].scrollIntoView(true);", apply_button)
        apply_button.click()

        wait_for_spinner_to_disappear(driver)
        time.sleep(0.2)

        remove_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Remove promotional code')]")
        print(f"✅ Promo code worked: {code}")
        successful_codes.append(code)

        driver.execute_script("arguments[0].click();", remove_link)
        time.sleep(1)

    except:
        print(f"❌ Invalid promo code: {code}")

driver.quit()

