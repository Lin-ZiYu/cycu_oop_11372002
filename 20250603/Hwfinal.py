# -*- coding: utf-8 -*-
"""
This module retrieves bus stop data for all routes from the Taipei eBus website,
saves the rendered HTML files for each route, and generates a CSV file with route details.
"""
import os
import pandas as pd
from bs4 import BeautifulSoup


class taipei_route_info:
    """
    Manages fetching, parsing, and storing bus stop data for a specified route and direction.
    """
    def __init__(self, route_id: str, direction: str = 'go', html_content: str = None):
        self.route_id = route_id
        self.direction = direction
        self.content = html_content

        if self.direction not in ['go', 'come']:
            raise ValueError("Direction must be 'go' or 'come'")

    def parse_stations(self) -> list:
        """
        Parses station names from the HTML content for the specified route and direction.
        """
        soup = BeautifulSoup(self.content, 'html.parser')

        # 根據方向選擇正確的區塊
        if self.direction == 'go':
            route_div = soup.find('div', id='GoDirectionRoute')
        elif self.direction == 'come':
            route_div = soup.find('div', id='BackDirectionRoute')
        else:
            raise ValueError("Direction must be 'go' or 'come'")

        if not route_div:
            print(f"❌ No route data found for direction {self.direction}.")
            return []

        # 提取車站名稱
        station_names = []
        for station in route_div.find_all('span', class_='auto-list-stationlist-place'):
            station_names.append(station.text.strip())

        return station_names


def fetch_all_routes_from_html(html_file_path: str) -> list:
    """
    Reads all bus routes from a local HTML file.
    """
    with open(html_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    soup = BeautifulSoup(content, 'html.parser')
    routes = []
    for route in soup.find_all('li'):
        link = route.find('a')
        if link and 'javascript:go' in link.get('href', ''):
            route_id = link['href'].split("'")[1]  # 提取 route_id
            route_name = link.text.strip()  # 提取公車名稱
            routes.append({'route_id': route_id, 'route_name': route_name})
    return routes


if __name__ == "__main__":
    # 指定 HTML 檔案路徑
    html_file_path = "c:/Users/User/Desktop/cycu_oop_11372002/20250603/all_routes.html"
    output_directory = "c:/Users/User/Desktop/cycu_oop_11372002/data"
    output_csv_path = "c:/Users/User/Desktop/cycu_oop_11372002/20250603/all_routes_stations.csv"

    # 從 HTML 檔案抓取所有公車路線
    all_routes = fetch_all_routes_from_html(html_file_path)

    # 檢查是否成功解析路線
    if not all_routes:
        print("❌ No routes found in the HTML file.")
        exit()

    # 初始化 DataFrame
    all_data = []

    for route in all_routes:
        route_id = route['route_id']
        route_name = route['route_name']
        print(f"Processing route: {route_name} ({route_id})")

        try:
            # 讀取去程資料
            route_info = taipei_route_info(
                route_id=route_id,
                direction="go",
                html_content=open(f"{output_directory}/ebus_taipei_{route_id}.html", 'r', encoding='utf-8').read()
            )
            go_station_names = route_info.parse_stations()

            # 讀取回程資料
            route_info.direction = "come"
            route_info.content = open(f"{output_directory}/ebus_taipei_{route_id}.html", 'r', encoding='utf-8').read()
            come_station_names = route_info.parse_stations()

            # 添加到總資料
            for station in go_station_names:
                all_data.append({
                    "公車名稱": route_name,
                    "方向": "去程",
                    "車站名稱": station
                })

            for station in come_station_names:
                all_data.append({
                    "公車名稱": route_name,
                    "方向": "回程",
                    "車站名稱": station
                })

        except Exception as e:
            print(f"Error processing route {route_name}: {e}")

    # 將所有資料存入 DataFrame
    final_df = pd.DataFrame(all_data)

    # 儲存到 CSV
    final_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
    print(f"✅ Saved all routes station names to {output_csv_path}")