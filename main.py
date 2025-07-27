import re
import time
import nltk
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from nltk.corpus import stopwords

# Download stopwords if not already
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


# Custom stopwords (for filtering website-specific filler words)
USER_STOPWORD = {'accept', 'access', 'accessed', 'accessibility', 'accessible', 'account', 'ages', 'agree', 
                  'alerts', 'assistive', 'audio', 'auditorium', 'available', 'buy', 'camera', 'captioned', 
                  'captions','buy', 'camera', 'captioned', 'captions', 'cast', 'choose', 'community', 'company', 
                  'conditions', 'conducted', 'cookies', 'dates', 'described', 'displayed', 'english', 'event', 
                  'events', 'experience', 'filter', 'free', 'front', 'guarantee', 'guests', 'guidance', 'guidelines', 
                  'handheld', 'hear', 'help', 'hour', 'incorporated', 'info', 'information', 'interpreted', 'interval',
                  'join', 'know', 'language', 'latest', 'learning', 'less', 'let', 'lift', 'limited', 'listening', 
                  'loud', 'main', 'manage', 'menu', 'minutes', 'monday', 'new', 'news', 'notice', 'number', 'october',
                  'one', 'page', 'performances', 'please', 'policy', 'preferences', 'priority', 'post', 'privacy','production',
                  'receive', 'registered', 'reject', 'requirements', 'returns', 'routes', 'saturday', 'screen', 
                  'seats', 'see', 'september', 'shop', 'show', 'sign', 'signal', 'staff', 'stage', 'stalls', 'starts', 
                  'step', 'steps', 'stream', 'suitable', 'sunday', 'support', 'take', 'terms', 'tuesday' ,'thursday', 'ticket', 'tickets'
                  'wednesday', 'yes', 'visit', 'use', 'website'}


def wait_for_spinner_to_disappear(driver, timeout=10):
    try:
        WebDriverWait(driver, timeout).until_not(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='general__Loading']")))
    except:
        print("Spinner did not disappear in time.")

# Setup Headless Chrome ---
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--log-level=3")
options.add_argument("--disable-logging")
options.add_experimental_option("excludeSwitches", ["enable-logging"])

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


url = 'https://www.rbo.org.uk/tickets-and-events/tosca-oliver-mears-dates'
driver.get(url)
time.sleep(4)  # Wait for JS and cookie popup to load

# Accept cookies 
try:
    accept_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept')]")
    accept_btn.click()
    time.sleep(2)
except:
    pass  # No cookie popup

# Click all 'Show all' links (which are <a> tags)
try:
    show_all_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Show all')]")
    # print(f"Found {len(show_all_links)} 'Show all' links.")
    for link in show_all_links:
        driver.execute_script("arguments[0].click();", link)
        time.sleep(0.5)
except Exception as e:
    print("Couldn't click 'Show all' links:", e)

# Grab fully-rendered HTML and close browser
html = driver.page_source

# Parse and clean HTML with BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Remove unwanted tags
for tag in soup(['script', 'style', 'meta', 'noscript']):
    tag.decompose()

# Extract all visible + revealed text
full_text = soup.get_text(separator=' ', strip=True)

# Remove all non-alphabetic tokens
cleaned_text = re.sub(r'\b[^a-zA-Z]+\b', ' ', full_text)
cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

# Extract lowercase word tokens (2+ letter words)
all_words = re.findall(r'\b[a-zA-Z]{2,}\b', cleaned_text)
all_words = [word.lower() for word in all_words]

# Remove stopwords
stop_words = set(stopwords.words('english'))
filtered_words = [word for word in all_words if (word not in stop_words and word not in USER_STOPWORD)]

# Get unique sorted word list
unique_words = sorted(set(filtered_words))

# print("\n\nFULL PAGE TEXT:")
# print(full_text)

# print(f"\nTotal Clean Words (after stopword removal): {len(filtered_words)}")
# print(f"Unique Words: {len(unique_words)}")
# print("\nWords:", unique_words)


'''*************************************************************'''
'''*************************************************************'''

# Generate promo codes using words from scraped content
promo_codes = []
for word in unique_words:
    # for i in range(45, 0, -5):
    for i in [30]:
        promo_codes.append(f"{word}{i}")
# print(promo_codes)

# Load the checkout page
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
    # Always re-find fresh input after DOM mutation
    input_box = wait.until(EC.presence_of_element_located((By.NAME, "promo-code-input")))
    driver.execute_script("arguments[0].scrollIntoView(true);", input_box)
    input_box.clear()
    input_box.send_keys(code)

    # Fresh apply button
    apply_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Apply promotional code')]")))
    driver.execute_script("arguments[0].scrollIntoView(true);", apply_button)
    apply_button.click()

    wait_for_spinner_to_disappear(driver)
    time.sleep(0.2)

    try:
        remove_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Remove promotional code')]")
        print(f"✅ Promo code worked: {code}")
        successful_codes.append(code)

        driver.execute_script("arguments[0].click();", remove_link)
        time.sleep(1)

    except:
        print(f"❌ Invalid promo code: {code}")

driver.quit()