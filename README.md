# Opera Discount Hunter

An automated tool that helps find valid promotional codes for the Royal Birmingham Opera (RBO) tickets by scraping content and testing potential promo codes.

## Features

- Scrapes event pages for relevant content
- Generates potential promo codes based on page content
- Automatically tests generated codes on the checkout page
- Identifies and reports working promotional codes
- Headless browser operation for faster execution

## Requirements

- Python 3.x
- Chrome browser
- Required Python packages:
  - selenium
  - beautifulsoup4
  - nltk
  - webdriver_manager

## Installation

1. Clone this repository
2. Install the required packages:
```bash
pip install selenium beautifulsoup4 nltk webdriver-manager
```

## Usage

1. Configure the script (optional):
   - Update the event page URL (line 55 in main.py)
   - Update the checkout URL (line 125 in main.py)
   - Adjust the promo code generation logic (lines 118-119 in main.py):
     - Currently generates codes with suffix "30" only
     - You can modify the loop to try different number suffixes

2. Run the script:
```bash
python main.py
```

The script will:
1. Open the specified RBO event page
2. Scrape and process the page content
3. Generate potential promo codes
4. Test each code on the checkout page
5. Print results showing which codes worked (✅) and which didn't (❌)

## Features in Detail

- **Content Scraping**: Uses BeautifulSoup to extract and clean page content
- **Text Processing**: Implements NLTK for text processing with custom stopwords
- **Automated Testing**: Uses Selenium WebDriver for automated promo code testing
- **Headless Operation**: Runs Chrome in headless mode for better performance

## Note

This tool is for educational purposes only. Please ensure you comply with the website's terms of service when using automated tools.

