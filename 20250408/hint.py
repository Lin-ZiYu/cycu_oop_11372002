# -*- coding: utf-8 -*-
import pandas as pd
import re
from playwright.sync_api import sync_playwright
import sqlite3


class BusRouteInfo:
    def __init__(self, routeid: str, direction: str = 'go'):
        self.rid = routeid
        self.content = None
        self.url = f'https://ebus.gov.taipei/Route/StopsOfRoute?routeid={routeid}'

        if direction not in ['go', 'come']:
            raise ValueError("Direction must be 'go' or 'come'")

        self.direction = direction

        self._fetch_content()
    

    def _fetch_content(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.url)
            
            if self.direction == 'come':
                page.click('a.stationlist-come-go-gray.stationlist-come')
            
            page.wait_for_timeout(3000)  # wait for 1 second
            self.content = page.content()
            browser.close()


        # Write the rendered HTML to a file route_{rid}.html
        with open(f"data/ebus_taipei_{self.rid}.html", "w", encoding="utf-8") as file:
            file.write(self.content)
import csv
from bs4 import BeautifulSoup

class BusRouteInfo:
    def __init__(self, routeid: str, direction: str = 'go'):
        self.rid = routeid
        self.content = None
        self.url = f'https://ebus.gov.taipei/Route/StopsOfRoute?routeid={routeid}'

        if direction not in ['go', 'come']:
            raise ValueError("Direction must be 'go' or 'come'")

        self.direction = direction

        self._fetch_content()
    

    def _fetch_content(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.url)
            
            if self.direction == 'come':
                page.click('a.stationlist-come-go-gray.stationlist-come')
            
            page.wait_for_timeout(3000)  # wait for 1 second
            self.content = page.content()
            browser.close()

        # Write the rendered HTML to a file route_{rid}.html
        with open(f"data/ebus_taipei_{self.rid}.html", "w", encoding="utf-8") as file:
            file.write(self.content)

    def parse_and_save_to_csv(self, output_file='bus_route_data.csv'):
        """
        解析網頁內容，提取公車站路線資料，並輸出為 CSV 格式。

        參數:
        - output_file: 輸出的 CSV 檔案名稱 (預設為 'bus_route_data.csv')
        """
        if not self.content:
            print("尚未取得網頁內容，無法解析。")
            return False

        try:
            # 使用 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(self.content, 'html.parser')

            # 假設站點資料在特定的 <table> 或 <div> 中
            stops_data = []
            stops_table = soup.find('table', {'class': 'stationlist-table'})  # 根據實際 HTML 結構調整
            if not stops_table:
                print("無法找到站點資料表格。")
                return False

            # 提取表格中的每一行數據
            rows = stops_table.find_all('tr')
            for row in rows[1:]:  # 跳過表頭
                cols = row.find_all('td')
                if len(cols) >= 6:
                    arrival_info = cols[0].text.strip()
                    stop_number = cols[1].text.strip()
                    stop_name = cols[2].text.strip()
                    stop_id = cols[3].text.strip()
                    latitude = cols[4].text.strip()
                    longitude = cols[5].text.strip()
                    stops_data.append([arrival_info, stop_number, stop_name, stop_id, latitude, longitude])

            # 將資料寫入 CSV 檔案
            with open(output_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # 寫入標題
                writer.writerow(["arrival_info", "stop_number", "stop_name", "stop_id", "latitude", "longitude"])
                # 寫入資料
                writer.writerows(stops_data)

            print(f"資料已成功儲存至 {output_file}")
            return True

        except Exception as e:
            print(f"解析或儲存資料時發生錯誤: {e}")
            return False

# 範例使用
if __name__ == "__main__":
    route_id = input("請輸入公車代碼 (例如 '0100000A00'): ")
    direction = input("請輸入方向 ('go' 或 'come'): ")
    output_file = "bus_route_data.csv"

    try:
        bus_info = BusRouteInfo(routeid=route_id, direction=direction)
        success = bus_info.parse_and_save_to_csv(output_file=output_file)
        if success:
            print(f"公車路線資料已儲存至 {output_file}")
        else:
            print("無法取得或解析公車路線資料。")
    except Exception as e:
        print(f"發生錯誤: {e}")