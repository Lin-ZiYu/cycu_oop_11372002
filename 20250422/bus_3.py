import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import geopandas as gpd
import matplotlib.pyplot as plt
import difflib  # 用於模糊匹配

def fetch_bus_stops_by_route(route_name):
    url = f"https://bus.pcrest.tw/?route={route_name}"
    print(f"正在抓取公車路線資料：{url}")

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

    # 儲存資料到清單
    bus_stops = []
    for stop in soup.find_all("a"):
        if stop.get("class") == ["auto-list-link", "auto-list-stationlist-link"]:
            stop_info = {}
            for i in stop.find_all("span"):
                if i.get("class") == ["auto-list-stationlist-place"]:
                    stop_info["站名"] = i.text.strip()
                if i.get("class") == ["auto-list-stationlist-number"]:
                    stop_info["站序"] = i.text.strip()
            bus_stops.append(stop_info)

    driver.quit()
    return bus_stops

def display_bus_stops(bus_stops):
    print("以下是該幹線的站點清單：")
    for stop in bus_stops:
        print(f"站序: {stop.get('站序', '未知')} - 站名: {stop.get('站名', '未知')}")

def fuzzy_match(name, candidates):
    """使用 difflib 進行模糊匹配"""
    matches = difflib.get_close_matches(name, candidates, n=1, cutoff=0.6)
    return matches[0] if matches else None

def draw_bus_route_from_geojson(geojson_file, route_name, output_file):
    # 讀取 GeoJSON 檔案
    gdf = gpd.read_file(geojson_file)

    # 確認 GeoJSON 檔案的欄位名稱
    print("GeoJSON 欄位名稱:", gdf.columns)

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

    # 指定 GeoJSON 檔案和輸出的 PNG 檔案
    geojson_file = "C:/Users/User/Desktop/cycu_oop_11372002/20250422/bus_stops.geojson"
    output_file = f"bus_route_{route_name}.png"

    # 繪製並儲存路線圖
    draw_bus_route_from_geojson(geojson_file, route_name, output_file)