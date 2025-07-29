# scrape_words.py

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

USER_STOPWORD = {
    'accept', 'access', 'accessed', 'accessibility', 'accessible', 'account', 'ages', 'agree', 'alerts',
    'assistive', 'audio', 'auditorium', 'available', 'buy', 'camera', 'captioned', 'captions', 'cast',
    'choose', 'community', 'company', 'conditions', 'conducted', 'cookies', 'dates', 'described',
    'displayed', 'english', 'event', 'events', 'experience', 'filter', 'free', 'front', 'guarantee',
    'guests', 'guidance', 'guidelines', 'handheld', 'hear', 'help', 'hour', 'incorporated', 'info',
    'information', 'interpreted', 'interval', 'join', 'know', 'language', 'latest', 'learning', 'less',
    'let', 'lift', 'limited', 'listening', 'loud', 'main', 'manage', 'menu', 'minutes', 'monday', 'new',
    'news', 'notice', 'number', 'october', 'one', 'page', 'performances', 'please', 'policy', 'preferences',
    'priority', 'post', 'privacy', 'production', 'receive', 'registered', 'reject', 'requirements', 'returns',
    'routes', 'saturday', 'screen', 'seats', 'see', 'september', 'shop', 'show', 'sign', 'signal', 'staff',
    'stage', 'stalls', 'starts', 'step', 'steps', 'stream', 'suitable', 'sunday', 'support', 'take', 'terms',
    'tuesday', 'thursday', 'ticket', 'tickets', 'wednesday', 'yes', 'visit', 'use', 'website'
}

def wait_for_spinner_to_disappear(driver, timeout=10):
    try:
        WebDriverWait(driver, timeout).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='general__Loading']"))
        )
    except:
        print("Spinner did not disappear in time.")

# Setup Headless Chrome
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
time.sleep(4)

# Accept cookies 
try:
    accept_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept')]")
    accept_btn.click()
    time.sleep(2)
except:
    pass  # No cookie popup

# Click all "Show all" cast links
try:
    show_all_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Show all')]")
    # print(f"Found {len(show_all_links)} 'Show all' links.")
    for link in show_all_links:
        driver.execute_script("arguments[0].click();", link)
        time.sleep(0.5)
except Exception as e:
    print("Couldn't click 'Show all' links:", e)

html = driver.page_source
driver.quit()

# Parse and clean
soup = BeautifulSoup(html, 'html.parser')
for tag in soup(['script', 'style', 'meta', 'noscript']):
    tag.decompose()

full_text = soup.get_text(separator=' ', strip=True)

# Remove all non-alphabetic tokens
cleaned_text = re.sub(r'\b[^a-zA-Z]+\b', ' ', full_text)
cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

# Extract lowercase word tokens (2+ letter words)
all_words = re.findall(r'\b[a-zA-Z]{2,}\b', cleaned_text)
all_words = [word.lower() for word in all_words]

# Remove stopwords
stop_words = set(stopwords.words('english'))
filtered_words = [word for word in all_words if word not in stop_words and word not in USER_STOPWORD]

# Get unique sorted word list
unique_words = sorted(set(filtered_words))

# print("\n\nFULL PAGE TEXT:")
# print(full_text)

# print(f"\nTotal Clean Words (after stopword removal): {len(filtered_words)}")
# print(f"Unique Words: {len(unique_words)}")
# print("\nWords:", unique_words)

# Save to file
with open("unique_words.txt", "w", encoding="utf-8") as f:
    for word in unique_words:
        f.write(f"{word}\n")

print(f"✅ Saved {len(unique_words)} unique words to 'unique_words.txt'")
