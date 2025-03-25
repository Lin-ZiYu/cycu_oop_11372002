import requests
from bs4 import BeautifulSoup

def get_bus_arrival_time(route_id, stop_name):
    url = f"https://pda5284.gov.taipei/MQS/route.jsp?rid={route_id}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve data")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 打印抓取到的 HTML 以便檢查
    # print(soup.prettify())
    
    # 根據實際的網頁結構來解析資料，這裡假設有一個 class 為 'stop' 的元素包含站牌名稱
    stops = soup.find_all(class_='stop')
    
    for stop in stops:
        if stop_name in stop.get_text():
            # 找到包含站牌名稱的元素後，查找其下的到站時間
            arrival_time = stop.find_next(class_='arrival-time')
            if arrival_time:
                print(f"{stop_name} 到站時間: {arrival_time.get_text()}")
                return
    print(f"No arrival times found for stop: {stop_name}")

if __name__ == "__main__":
    route_id = "10851"  # 固定的路線編號
    stop_name = input("請輸入站牌名稱: ")
    get_bus_arrival_time(route_id, stop_name)