from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# 初始化 WebDriver
def init_driver():
    service = Service(ChromeDriverManager().install())  # 自動下載並安裝 ChromeDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 無頭模式
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# 取得所有公車路線
def get_all_bus_line(driver):
    driver.get("https://ebus.gov.taipei/ebus")
    time.sleep(1)  # 等待頁面加載

    soup = BeautifulSoup(driver.page_source, "html.parser")
    all_bus_line = {}

    # 找到所有 <section class="busline">
    for section in soup.find_all("section", class_="busline"):
        for li in section.find_all("li"):
            a = li.find("a")
            if a:
                bus_line_name = a.text.strip()
                bus_line_id = a["href"].replace("javascript:go('", "").replace("')", "")
                all_bus_line[bus_line_name] = bus_line_id

    return all_bus_line

# 主程式
if __name__ == "__main__":
    driver = init_driver()
    try:
        # 呼叫函式取得所有公車路線
        all_bus_line = get_all_bus_line(driver)
        print("所有公車路線：")
        print(all_bus_line)
    finally:
        driver.quit()