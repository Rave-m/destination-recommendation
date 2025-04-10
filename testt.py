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

all_reviews = []

with open("helper/links.json", "r", encoding="utf-8") as f:
    links = json.load(f)

# Fungsi ambil semua review dari satu halaman
def ambil_review_di_halaman():
    reviews = []
    review_cards = driver.find_elements(By.CLASS_NAME, "ReviewCard_review_card__4_CXC")

    for card in review_cards:
        try:
            name = card.find_element(By.CLASS_NAME, "ReviewCard_customer_name__mwGEt").text
            rating = card.find_element(By.CLASS_NAME, "ReviewCard_review_card_header_right__riU1Q").text
            tanggal = card.find_element(By.CLASS_NAME, "ReviewCard_date__Nr8Lq").text
            komentar = card.find_element(By.CLASS_NAME, "ReadMoreComments_review_card_comment__R_W2B").text

            # Klik tombol "Selengkapnya" jika ada
            try:
                selengkapnya_btn = card.find_element(By.CLASS_NAME, "ReadMoreComments_read_more__r2ZQ7")
                driver.execute_script("arguments[0].click();", selengkapnya_btn)
                time.sleep(0.3)
            except:
                pass  # tombol tidak ditemukan, lanjutkan

            reviews.append({
                "name": name,
                "komentar": komentar,
                "rating": rating,
                "tanggal": tanggal
            })
        except Exception as e:
            print("Gagal mengambil data dari card:", e)
    return reviews

# Loop buka satu per satu
for idx, link in enumerate(links):
    print(f"[{idx+1}] Membuka: {link['title']} - {link['link']}")
    driver.get(link['link'])
    
    # Tunggu elemen muncul
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "rr___ReviewWidget-module__review_list___RQic3"))
    )

    try:
        review_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Review']]"))
        )
        review_button.click()
        
        # Klik tombol "Lihat semua"
        try:
            lihat_semua_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="see-all"]'))
            )
            driver.execute_script("arguments[0].click();", lihat_semua_btn)
            
            try:
                halaman_ke = 1
                
                # Tunggu konten review muncul (misalnya berdasarkan class konten review)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ResponsiveLayout_responsive_container__SkabW"))
                )
                
                while True:
                    print(f"\n📄 Ambil review dari {link['title']} halaman {halaman_ke}...")
                    
                    # Scroll untuk pastikan semua review dimuat
                    for _ in range(5):
                        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
                        time.sleep(1)

                    # Ambil review dan tambahkan ke list
                    all_reviews.extend({
                        "title": link['title'],
                        "review": ambil_review_di_halaman()
                    })

                    try:
                        next_btn = driver.find_element(By.CSS_SELECTOR, '[data-testid="chevron-right-pagination"]')
                        next_btn_class = next_btn.get_attribute("class")

                        if "ReviewPagination_inactive__0UEop" in next_btn_class:
                            print("✅ Halaman terakhir. Tidak ada lagi halaman selanjutnya.")
                            break
                        else:
                            driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
                            next_btn.click()
                            time.sleep(2)
                            halaman_ke += 1
                    except Exception as e:
                        print("❌ Gagal navigasi ke halaman berikutnya:", e)
                        break
            
            except Exception as e:
                print("Gagal menunggu konten review muncul:", e)
                
        except Exception as e:
            print("Gagal klik 'Lihat semua' atau konten tidak muncul:", e)
            
    except Exception as e:
        print("Gagal klik tombol 'Review':", e)
        
    time.sleep(5)  # Tunggu 5 detik sebelum lanjut ke link berikutnya
    
# Simpan ke file JSON
with open("helper/reviews.json", "w") as file:
    json.dump(all_reviews, file, indent=4)

# Tutup browser
driver.quit()