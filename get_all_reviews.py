from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import json
import csv
import os

# Setup ChromeDriver
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

all_reviews = []
review_list = []

with open("helper/links.json", "r", encoding="utf-8") as f:
    links = json.load(f)

# Fungsi ambil semua review dari satu halaman
def ambil_review_di_halaman():
    reviews = []
    review_cards = driver.find_elements(By.CLASS_NAME, "ReviewCard_review_card__4_CXC")

    for card in review_cards:
        try:
            name = card.find_element(By.CLASS_NAME, "ReviewCard_customer_name__mwGEt").text
        except:
            name = "Anonim"

        try:
            rating = card.find_element(By.CLASS_NAME, "ReviewCard_review_card_header_right__riU1Q").text
        except:
            rating = ""

        try:
            tanggal = card.find_element(By.CLASS_NAME, "ReviewCard_date__Nr8Lq").text
        except:
            tanggal = ""

        try:
            komentar = card.find_element(By.CLASS_NAME, "ReadMoreComments_review_card_comment__R_W2B").text
        except:
            komentar = ""

        # Klik tombol "Selengkapnya" jika ada
        try:
            selengkapnya_btn = card.find_element(By.CLASS_NAME, "ReadMoreComments_read_more__r2ZQ7")
            driver.execute_script("arguments[0].click();", selengkapnya_btn)
            time.sleep(0.3)
        except:
            pass  # tombol tidak ditemukan, lanjutkan

        reviews.append({
            "username": name,
            "komentar": komentar,
            "rating": rating,
            "tanggal": tanggal
        })
            
    return reviews

def simpan_checkpoint(filepath="helper/checkpoint_reviews.csv", data=None):
    if data is None:
        data = review_list

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        fieldnames = ["nama_destinasi", "username", "komentar", "rating", "tanggal"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for item in data:
            writer.writerow({
                "nama_destinasi": item["nama_destinasi"],
                "username": item["review"]["username"],
                "komentar": item["review"]["komentar"],
                "rating": item["review"]["rating"],
                "tanggal": item["review"]["tanggal"]
            })

checkpoint_file = "helper/checkpoint_reviews.csv"
sudah_diproses = set()

if os.path.exists(checkpoint_file):
    with open(checkpoint_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            review_list.append({
                "nama_destinasi": row["nama_destinasi"],
                "review": {
                    "username": row["username"],
                    "komentar": row["komentar"],
                    "rating": row["rating"],
                    "tanggal": row["tanggal"]
                }
            })
            sudah_diproses.add(row["nama_destinasi"])
    print(f"📌 Lanjut dari checkpoint. Sudah ada {len(sudah_diproses)} destinasi.")
    
# Loop buka satu per satu
for idx, link in enumerate(links):
    if link["title"] in sudah_diproses:
        print(f"➡️  Skip (sudah diproses): {link['title']}")
        continue
    
    print(f"[{idx+1}] Membuka: {link['title']} - {link['link']}")
    driver.get(link['link'])
    all_reviews = []

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "rr___ReviewWidget-module__review_list___RQic3"))
        )

        review_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Review']]"))
        )
        review_button.click()

        lihat_semua_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="see-all"]'))
        )
        driver.execute_script("arguments[0].click();", lihat_semua_btn)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ResponsiveLayout_responsive_container__SkabW"))
        )

        halaman_ke = 1
        while True:
            print(f"\n📄 Ambil review dari {link['title']} halaman {halaman_ke}...")
            for _ in range(5):
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
                time.sleep(1)

            all_reviews.extend(ambil_review_di_halaman())

            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, '[data-testid="chevron-right-pagination"]')
                if "ReviewPagination_inactive__0UEop" in next_btn.get_attribute("class"):
                    break
                driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
                next_btn.click()
                time.sleep(2)
                halaman_ke += 1
            except:
                break

        for review in all_reviews:
            review_list.append({
                "nama_destinasi": link['title'],
                "review": review
            })
        # 🧠 Simpan checkpoint setelah tiap destinasi
        simpan_checkpoint()

    except Exception as e:
        print(f"❌ Gagal mengambil review dari {link['title']}:", e)

    time.sleep(3)

# Simpan ke file CSV
with open("results/reviews.csv", "w", newline="", encoding="utf-8") as file:
    fieldnames = ["nama_destinasi", "username", "komentar", "rating", "tanggal"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    for item in review_list:
        writer.writerow({
            "nama_destinasi": item["nama_destinasi"],
            "username": item["review"]["username"],
            "komentar": item["review"]["komentar"],
            "rating": item["review"]["rating"],
            "tanggal": item["review"]["tanggal"]
        })

# Tutup browser
driver.quit()