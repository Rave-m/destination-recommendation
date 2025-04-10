from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import json

# Setup ChromeDriver
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

# Target URL
url = "https://www.tiket.com/to-do/search?utm_logic=7A36C737EFE4D2E6585E2A6D6B6613BE&utm_section=pageModule%3B64d367332ad4ad000186bd44&publicIds=yogyakarta-province-108001534490276304&productAllCategoryCodes=ATTRACTION"
driver.get(url)

# Tunggu elemen muncul
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "ProductCardSearch_product_card_search__haSGm"))
)

# Scroll ke bawah untuk memastikan semua data dimuat
for _ in range(5):  # Sesuaikan jumlah scroll
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
    time.sleep(2)

# Ambil semua produk
cards = driver.find_elements(By.CLASS_NAME, "ProductCardSearch_product_card_search__haSGm")

# print (f"Total produk ditemukan: {len(cards)}")

base_url = "https://www.tiket.com"
all_links = []

for card in cards:
    try:
        title = card.find_element(By.TAG_NAME, "h2").text
    except Exception as e:
        title = "Gagal ambil title"
        
    
    try:
        href = card.get_attribute("href")
        if href.startswith("/"):
            href = base_url + href
            
    except Exception as e:
        print("Gagal ambil link:", e)
        
    all_links.append({
        "title": title,
        "link": href
    })


# Tampilkan hasil
print(f"Total link ditemukan: {len(all_links)}")

# Simpan ke file JSON
with open("helper/links.json", "w") as file:
    json.dump(all_links, file, indent=4)

# Tutup browser
driver.quit()