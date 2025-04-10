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

# URL review
url = "https://www.tiket.com/review?product_type=TODO&searchType=INVENTORY&inventoryIds=5e5d080d0dcd8875a520ce72%2C65357e72f4674e19b0df36f2&reviewSubmitColumn=RATING_SUMMARY"
driver.get(url)

# Tunggu elemen utama muncul
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "ResponsiveLayout_responsive_container__SkabW"))
    )
except:
    print("Timeout: Data tidak ditemukan!")
    driver.quit()
    exit()

semua_review = []
halaman_ke = 1

while True:
    print(f"\n📄 Ambil review dari halaman {halaman_ke}...")

    # Scroll untuk pastikan semua review dimuat
    for _ in range(5):
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
        time.sleep(1)

    # Ambil review dan tambahkan ke list
    semua_review.extend(ambil_review_di_halaman())

    # Coba klik tombol "Next"
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

# Tampilkan hasil
print(f"\n🎉 Total review terkumpul: {len(semua_review)}\n")
for idx, review in enumerate(semua_review, 1):
    print(f"{idx}. [{review['tanggal']}] Rating: {review['rating']} - Komentar: {review['komentar']}")

# Tutup browser
driver.quit()
