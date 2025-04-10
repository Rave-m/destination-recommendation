from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

# URL target
url = "https://www.tiket.com/to-do/search?utm_logic=7A36C737EFE4D2E6585E2A6D6B6613BE&utm_section=pageModule%3B64d367332ad4ad000186bd44&publicIds=yogyakarta-province-108001534490276304&productAllCategoryCodes=ATTRACTION"
driver.get(url)

data = []

# Tunggu hingga elemen produk muncul
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "ProductCardSearch_product_card_search__haSGm"))
    )
except:
    print("Timeout: Data tidak ditemukan!")
    driver.quit()
    exit()

# Scroll ke bawah untuk memastikan semua data dimuat
for _ in range(5):  # Sesuaikan jumlah scroll
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
    time.sleep(2)

# Ambil semua produk
products = driver.find_elements(By.CLASS_NAME, "ProductCardSearch_product_card_search__haSGm")

# Looping dan ekstrak data
for product in products:
    try:
        title = product.find_element(By.TAG_NAME, "h2").text
    except:
        title = "No title"

    try:
        location = product.find_element(By.CLASS_NAME, "product-info_info_text__JT1m3").text
    except:
        location = "No location"

    try:
        price = product.find_element(By.CLASS_NAME, "ProductCardTTD_final_price_wrapper__QX7xp").text
    except:
        price = "No price"

    try:
        rating = product.find_element(By.CLASS_NAME, "ProductCardTTD_product_info_variant__0XRBt").text
    except:
        rating = "No rating"

    print(f"Title: {title}")
    print(f"Location: {location}")
    print(f"Price: {price}")
    print(f"Rating: {rating}")
    print("-" * 50)
    
    data.append({
        "title": title,
        "location": location,
        "price": price,
        "rating": rating
    })

# Tutup browser setelah selesai
driver.quit()

print(data)