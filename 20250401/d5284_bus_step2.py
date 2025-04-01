from requests_html import HTMLSession
import requests
import html
import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def get_stop_info(stop_link: str) -> dict:
    """
    使用 Playwright 模擬瀏覽器操作，提取指定車站的公車到站時間。
    """
    stop_id = stop_link.split("=")[1]
    url = f'https://pda5284.gov.taipei/MQS/{stop_link}'

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        # 等待頁面加載完成
        page.wait_for_timeout(2000)
        # 提取到站時間資訊
        bus_times = page.locator(".stopInfo").all_text_contents()
        browser.close()

    return {"stop_id": stop_id, "bus_times": bus_times}


def get_bus_route(rid):
    """
    提取指定路線的去程與回程資料。
    """
    url = f'https://pda5284.gov.taipei/MQS/route.jsp?rid={rid}'

    # 發送 GET 請求
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        tables = soup.find_all("table")

        go_rows = []
        back_rows = []

        # 遍歷表格，提取去程與回程資料
        for table in tables:
            for tr in table.find_all("tr", class_=["ttego1", "ttego2"]):
                td = tr.find("td")
                if td:
                    stop_name = html.unescape(td.text.strip())
                    stop_link = td.find("a")["href"] if td.find("a") else None
                    go_rows.append({"stop_name": stop_name, "stop_link": stop_link})

            for tr in table.find_all("tr", class_=["tteback1", "tteback2"]):
                td = tr.find("td")
                if td:
                    stop_name = html.unescape(td.text.strip())
                    stop_link = td.find("a")["href"] if td.find("a") else None
                    back_rows.append({"stop_name": stop_name, "stop_link": stop_link})

        # 檢查是否有足夠的資料
        if not go_rows or not back_rows:
            raise ValueError("Insufficient table data found.")

        # 轉換為 DataFrame
        go_dataframe = pd.DataFrame(go_rows)
        back_dataframe = pd.DataFrame(back_rows)

        return go_dataframe, back_dataframe
    else:
        raise ValueError(f"Failed to download webpage. HTTP status code: {response.status_code}")


# 主程式
if __name__ == "__main__":
    rid = "10417"  # 測試路線 ID
    try:
        # 提取去程與回程資料
        go_df, back_df = get_bus_route(rid)
        print("去程資料:")
        print(go_df)
        print("\n回程資料:")
        print(back_df)

        # 輸入當前車站名稱和目標車站名稱
        current_stop = input("\n請輸入當前車站名稱: ")
        target_stop = input("請輸入目標車站名稱: ")

        # 查詢當前車站連結
        current_stop_link = None
        for _, row in pd.concat([go_df, back_df]).iterrows():
            if row["stop_name"] == current_stop:
                current_stop_link = row["stop_link"]
                break

        if current_stop_link:
            # 提取當前車站的公車到站時間
            stop_info = get_stop_info(current_stop_link)
            print(f"\n當前車站 ID: {stop_info['stop_id']}")
            print("公車到站時間:")
            for time in stop_info["bus_times"]:
                print(time)

            # 查詢能到達目標車站的公車
            buses_to_target = []
            for _, row in pd.concat([go_df, back_df]).iterrows():
                if row["stop_name"] == target_stop:
                    buses_to_target.append(row)

            if buses_to_target:
                print(f"\n能到達目標車站 {target_stop} 的公車:")
                for bus in buses_to_target:
                    print(f"公車: {bus['stop_name']}, 連結: {bus['stop_link']}")
            else:
                print(f"未找到能到達目標車站 {target_stop} 的公車。")
        else:
            print("未找到當前車站的資料。")

    except ValueError as e:
        print(f"Error: {e}")