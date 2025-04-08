import requests
import csv
import os

def fetch_bus_route_data(route_id, output_file='bus_route_data.csv'):
    """
    從臺北市公開網站取得公車路線資料，並輸出為 CSV 格式。

    參數:
    - route_id: 公車代碼 (例如 '0100000A00')
    - output_file: 輸出的 CSV 檔案名稱 (預設為 'bus_route_data.csv')

    回傳:
    - 成功時回傳 True，失敗時回傳 False。
    """
    try:
        # 定義 API URL
        url = f"https://ebus.gov.taipei/Route/StopsOfRoute?routeid={route_id}"
        
        # 發送 GET 請求
        response = requests.get(url)
        response.raise_for_status()  # 檢查請求是否成功
        
        # 解析 JSON 資料
        data = response.json()
        
        # 檢查資料是否包含所需欄位
        if 'Stops' not in data:
            print("無法取得公車站點資料。")
            return False
        
        # 提取站點資料
        stops = data['Stops']
        parsed_data = []
        for stop in stops:
            arrival_info = stop.get('arrival_info', '未知')
            stop_number = stop.get('stop_number', '未知')
            stop_name = stop.get('stop_name', '未知')
            stop_id = stop.get('stop_id', '未知')
            latitude = stop.get('latitude', '未知')
            longitude = stop.get('longitude', '未知')
            parsed_data.append([arrival_info, stop_number, stop_name, stop_id, latitude, longitude])
        
        # 將資料寫入 CSV 檔案
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # 寫入標題
            writer.writerow(["arrival_info", "stop_number", "stop_name", "stop_id", "latitude", "longitude"])
            # 寫入資料
            writer.writerows(parsed_data)
        
        print(f"資料已成功儲存至 {output_file}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"網路請求錯誤: {e}")
        return False
    except Exception as e:
        print(f"發生錯誤: {e}")
        return False

# 範例使用
if __name__ == "__main__":
    # 輸入公車代碼
    route_id = input("請輸入公車代碼 (例如 '0100000A00'): ")
    output_file = "bus_route_data.csv"
    
    # 呼叫函數
    success = fetch_bus_route_data(route_id, output_file)
    if success:
        print(f"公車路線資料已儲存至 {output_file}")
    else:
        print("無法取得公車路線資料。")