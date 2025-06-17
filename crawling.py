import json
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

json_file = "output.json"

def load_data():
    if os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_data(data):
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Khởi tạo driver
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://www.uit.edu.vn/hoc-tap-nghien-cuu"  # Thay bằng URL thật
driver.get(url)
main_tab = driver.current_window_handle

total_posts_collected = 0

while True:
    links = driver.find_elements(By.CSS_SELECTOR, "h2 a")
    data = load_data()

    count_this_page = 0

    for i, link in enumerate(links):
        href = link.get_attribute("href")
        if not href:
            continue

        if any(post.get("url") == href for post in data):
            print(f"⚠️ Bỏ qua bài đã có trong JSON: {href}")
            continue

        driver.execute_script("window.open(arguments[0], '_blank');", href)
        time.sleep(1)
        driver.switch_to.window(driver.window_handles[-1])

        try:
            time.sleep(2)
            title = driver.find_element(By.TAG_NAME, "h1").text
            date = driver.find_element(By.CSS_SELECTOR, "div.submitted span").text
            content = driver.find_element(By.CSS_SELECTOR, "div#content-body div.content div.content").text

            post = {
                "title": title,
                "date": date,
                "content": content,
                "url": href
            }

            data.append(post)
            save_data(data)

            print(f"✅ Lấy bài {total_posts_collected + 1}: {title}")

            total_posts_collected += 1
            count_this_page += 1

            # Nếu đã lấy đủ 10 bài thì dừng vòng for, chuẩn bị sang trang mới
            if count_this_page >= 10:
                driver.close()
                driver.switch_to.window(main_tab)
                break

        except Exception as e:
            print(f"❌ Lỗi lấy dữ liệu {href}: {e}")

        driver.close()
        driver.switch_to.window(main_tab)

    else:
        # Nếu vòng for kết thúc mà chưa break (chưa đủ 10 bài), lấy hết bài trên trang

        # Kiểm tra có trang kế tiếp không
        try:
            next_li = driver.find_element(By.CSS_SELECTOR, "li.pager-next")
            next_link = next_li.find_element(By.TAG_NAME, "a")
            next_href = next_link.get_attribute("href")
            if not next_href:
                print("❌ Không tìm thấy link trang kế tiếp, kết thúc.")
                break
            print("➡️ Chuyển sang trang tiếp theo:", next_href)
            driver.get(next_href)
            time.sleep(2)
            continue  # quay lại vòng while lấy tiếp
        except NoSuchElementException:
            print("✅ Không còn trang kế tiếp, kết thúc thu thập.")
            break

    # Nếu break ra do đủ 10 bài
    # cũng kiểm tra trang kế tiếp để sang trang mới
    try:
        next_li = driver.find_element(By.CSS_SELECTOR, "li.pager-next")
        next_link = next_li.find_element(By.TAG_NAME, "a")
        next_href = next_link.get_attribute("href")
        if not next_href:
            print("❌ Không tìm thấy link trang kế tiếp, kết thúc.")
            break
        print("➡️ Chuyển sang trang tiếp theo:", next_href)
        driver.get(next_href)
        time.sleep(2)
    except NoSuchElementException:
        print("✅ Không còn trang kế tiếp, kết thúc thu thập.")
        break

driver.quit()
print(f"✅ Hoàn thành thu thập tổng cộng {total_posts_collected} bài")
