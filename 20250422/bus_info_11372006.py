# %%

import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

def bus_info():
    # 使用者輸入公車路線代碼
    bus_code = input("請輸入id或是直接enter(默認0100026540): ") or "0100026540"
    url = "https://ebus.gov.taipei/Route/StopsOfRoute?routeid=" + bus_code
    print(url)

# 設定無頭模式（不開啟瀏覽器畫面）
    options = Options()
    options.add_argument("--headless")

# 開啟 Chrome 瀏覽器
    driver = webdriver.Chrome(options=options)

# 開啟目標頁面
    driver.get(url)

# 等待 JavaScript 執行
    time.sleep(3)  # 可以改成 WebDriverWait 更穩定

# 抓下來的 HTML
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

# 儲存資料到 CSV 檔案
    with open("bus_stops.csv", "w", encoding="utf-8", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
    # 寫入表頭
        csvwriter.writerow(["公車到達時間", "車站序號", "車站名稱", "車站編號", "latitude", "longitude"])

        clo = False
        for stop in soup.find_all("a"):
            if stop.get("class") == ["auto-list-link", "auto-list-stationlist-link"]:
                row = []
                for i in stop.find_all("span"):
                    if i.get("class") == [
                    "auto-list-stationlist-position",
                    "auto-list-stationlist-position-none",
                ]:
                        row.append(i.text.strip())
                        continue
                if i.get("class") == [
                    "auto-list-stationlist-position",
                    "auto-list-stationlist-position-now",
                ]:
                        row.append(i.text.strip())
                        continue
                if i.get("class") == [
                    "auto-list-stationlist-position",
                    "auto-list-stationlist-position-time",
                ]:
                        row.append(i.text.strip())
                        continue
                if i.get("class") == ["auto-list-stationlist-position"]:
                        clo = True
                        break
                if i.get("class") == ["auto-list-stationlist-number"]:
                        row.append(i.text.strip())
                        continue
                if i.get("class") == ["auto-list-stationlist-place"]:
                        row.append(i.text.strip())
                        continue
                if clo:
                    break
                for i in stop.find_all("input"):
                    if i.get("id") == "item_UniStopId":
                        row.append(i.get("value"))
                        continue
                    if i.get("id") == "item_Latitude":
                        row.append(i.get("value"))
                        continue
                    if i.get("id") == "item_Longitude":
                        row.append(i.get("value"))
                        continue
                csvwriter.writerow(row)
                if clo:
                    break

    driver.quit()
    print("完成，請查看 bus_stops.csv")

# %%
