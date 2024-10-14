# SAGRADO NO BORRAR
# SCRAPING de ZONAPROP
# Imports
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup
import pandas as pd
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# Path to your geckodriver
geckodriver_path = 'C:/Users/Julian/Downloads/geckodriver-v0.35.0-win32/geckodriver.exe'

# Generate a random user agent using fake_useragent
ua = UserAgent()
user_agent = ua.random

# Start undetected Chrome driver
options = uc.ChromeOptions()
options.add_argument(f'user-agent={user_agent}')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-blink-features=AutomationControlled')

# How long to sleep
sleep_time = 3

# Run in normal (non-headless) mode to avoid detection
driver = uc.Chrome(options=options)

# List to store property data
properties = []

try:
    # Loop through the first 5 pages
    for page in range(1, 4):
        # Update the URL to include the page number
        if page == 1:
            url = 'https://www.zonaprop.com.ar/departamentos-venta-vicente-lopez-q.html'
        else:
            #pass
            url = f'https://www.zonaprop.com.ar/departamentos-venta-vicente-lopez-pagina-{page}.html'
        try:
            # Load the URL
            driver.get(url)
            print(f'Page {page} loaded successfully')
            time.sleep(sleep_time)  # Wait for loading

            # Scroll to the bottom of the page to ensure all content is loaded
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(sleep_time)  # Additional wait after scrolling

            # Wait for a known element to be present before proceeding
            WebDriverWait(driver, sleep_time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.PostingCardLayout-sc-i1odl-0'))
            )
            print('Content found on the page')

            # Get the page source
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            #print(soup.prettify())

            #Scraping logic
            n=1
            # Just for making sure each property is loading
            for i in soup.find_all('div', class_='PostingContainer-sc-i1odl-2'):
                print(f"Pag {page}, Propiedad {n}, en {i.find('div',class_='LocationAddress-sc-ge2uzh-0').text}")
                print("\n")
                n=n+1

            # Extract property data
            for item in soup.find_all('div', class_='PostingContainer-sc-i1odl-2'):
                price = item.find('div', class_='Price-sc-12dh9kl-3').get_text(strip=True) if item.find('div', class_='Price-sc-12dh9kl-3') else None
                expensas = item.find('div', class_='Expenses-sc-12dh9kl-1').get_text(strip=True) if item.find('div', class_='Expenses-sc-12dh9kl-1') else None
                location = item.find('div', class_='LocationAddress-sc-ge2uzh-0').get_text(strip=True) if item.find('div', class_='LocationAddress-sc-ge2uzh-0') else None
                neighborhood = item.find('h2', class_='LocationLocation-sc-ge2uzh-2').get_text(strip=True) if item.find('h2', class_='LocationLocation-sc-ge2uzh-2') else None
                size = item.select_one('h3[data-qa="POSTING_CARD_FEATURES"] > span:first-child').get_text(strip=True) if item.select_one('h3[data-qa="POSTING_CARD_FEATURES"] > span:first-child') else None
                features = [span.get_text(strip=True) for span in item.find_all('span', class_='PostingMainFeaturesBlock-sc-1uhtbxc-0 cHDgeO')] if item.find('span', class_='PostingMainFeaturesBlock-sc-1uhtbxc-0 cHDgeO') else []
                description_tag = item.find('h3', class_='PostingDescription-sc-i1odl-11')
                description = description_tag.get_text(strip=True) if description_tag else None
                link = 'https://www.zonaprop.com.ar' + description_tag.find('a')['href'] if description_tag and description_tag.find('a') else None
        
                # Append the data to the list
                properties.append({
                    'Price': price,
                    'Expensas': expensas,
                    'Location': location,
                    'Neighborhood': neighborhood,
                    'Size (m²)': size,
                    'Features': features,
                    'Description': description,
                    'Link': link,
                    'Page': page,
                    #'Size numeric': int(size.replace(' m2', '')),
                    #'Price numeric': int(price.replace('USD ',''))
                })


        except Exception as e:
            print(f"An error occurred on page {page}: {e}")

finally:
    driver.quit()  # Ensure the driver is closed after all iterations


# Convert to DataFrame
df = pd.DataFrame(properties)
print("DataFrame created")
print("\nDescription")
print(df.describe())
print("\nInfo")
print(df.info())
print("\nHead")
print(df.head)

# Export to Excel
path = 'C:/Users/Julian/Downloads'
filename = 'zonaproperties_deptos_vilo.xlsx'
df.to_excel(f'{path}/{filename}', index=False)

print(f"Data exported to {path}/{filename}")