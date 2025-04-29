import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import geopandas as gpd
import matplotlib.pyplot as plt
import difflib  # 用於模糊匹配
from matplotlib.offsetbox import OffsetImage, AnnotationBbox  # 用於繪製小人圖樣

def fetch_bus_stops_by_route(route_name):
    url = f"https://bus.pcrest.tw/?route={route_name}"
    print(f"正在抓取公車路線資料：{url}")

    # 設定無頭模式（不開啟瀏覽器畫面）
    options = Options()
    options.add_argument("--headless")

    # 開啟 Chrome 瀏覽器
    driver = webdriver.Chrome(options=options)

    try:
        # 開啟目標頁面
        driver.get(url)

        # 等待 JavaScript 執行
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "auto-list-link"))
        )

        # 抓下來的 HTML
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # 儲存資料到清單
        bus_stops = []
        for stop in soup.find_all("a", class_="auto-list-link auto-list-stationlist-link"):
            stop_info = {}
            for i in stop.find_all("span"):
                if i.get("class") == ["auto-list-stationlist-place"]:
                    stop_info["站名"] = i.text.strip()
                if i.get("class") == ["auto-list-stationlist-number"]:
                    stop_info["站序"] = i.text.strip()
            if stop_info:
                bus_stops.append(stop_info)

        return bus_stops
    except Exception as e:
        print(f"錯誤：{e}")
        return []
    finally:
        driver.quit()

def display_bus_stops(bus_stops):
    print("以下是該幹線的站點清單：")
    for idx, stop in enumerate(bus_stops):
        print(f"{idx + 1}. 站序: {stop.get('站序', '未知')} - 站名: {stop.get('站名', '未知')}")

def fuzzy_match(name, candidates):
    """使用 difflib 進行模糊匹配"""
    matches = difflib.get_close_matches(name, candidates, n=1, cutoff=0.6)
    return matches[0] if matches else None

def draw_bus_route_with_marker(geojson_file, route_name, output_file, selected_stop_name):
    # 讀取 GeoJSON 檔案
    gdf = gpd.read_file(geojson_file)

    # 確保 BSM_BUSSTO 欄位為字串類型，並處理 NaN 值
    gdf['BSM_BUSSTO'] = gdf['BSM_BUSSTO'].astype(str).fillna('')

    # 過濾出與幹線名稱匹配的路線
    filtered_routes = gdf[gdf['BSM_BUSSTO'].str.contains(route_name, na=False)]

    # 檢查是否有匹配的路線
    if filtered_routes.empty:
        print(f"錯誤：無法在 GeoJSON 檔案中找到幹線名稱為 '{route_name}' 的路線。")
        return

    # 繪製路線圖
    fig, ax = plt.subplots(figsize=(10, 10))
    filtered_routes.plot(ax=ax, color='blue', linewidth=2, label=route_name)

    # 在地圖上標記選定的站點
    stop_row = gdf[gdf['BSM_BUSSTO'] == selected_stop_name]
    if not stop_row.empty:
        stop_coords = stop_row.geometry.iloc[0].coords[0]
        img = OffsetImage(plt.imread("person_icon.png"), zoom=0.1)  # 小人圖樣
        ab = AnnotationBbox(img, stop_coords, frameon=False)
        ax.add_artist(ab)
        plt.scatter(*stop_coords, color='red', label=f"選定站點: {selected_stop_name}")

    plt.title(f"{route_name} 公車路線圖")
    plt.xlabel("經度")
    plt.ylabel("緯度")
    plt.legend()

    # 儲存為 PNG 檔案
    plt.savefig(output_file)
    plt.close()
    print(f"路線圖已儲存為 {output_file}")

if __name__ == "__main__":
    # 使用者輸入幹線名稱
    route_name = input("請輸入幹線名稱 (例如 基隆路幹線): ") or "基隆路幹線"

    # 抓取站名清單
    bus_stops = fetch_bus_stops_by_route(route_name)
    if not bus_stops:
        print("未能抓取到任何站點資料，請檢查路線名稱是否正確或網站是否可用。")
        exit()

    display_bus_stops(bus_stops)

    # 讓使用者選擇站名
    while True:
        try:
            selected_index = int(input("請選擇站點編號: ")) - 1
            if 0 <= selected_index < len(bus_stops):
                break
            else:
                print(f"請輸入 1 到 {len(bus_stops)} 之間的數字。")
        except ValueError:
            print("無效的輸入，請輸入數字。")

    selected_stop_name = bus_stops[selected_index]["站名"]

    # 指定 GeoJSON 檔案和輸出的 PNG 檔案
    geojson_file = "C:/Users/User/Desktop/cycu_oop_11372002/20250422/bus_stops.geojson"
    output_file = f"bus_route_{route_name}.png"

    # 繪製並儲存路線圖，並在地圖上標記選定站點
    draw_bus_route_with_marker(geojson_file, route_name, output_file, selected_stop_name)