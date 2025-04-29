# -*- coding: utf-8 -*-
"""
This module retrieves bus stop data for a specific route and direction from the Taipei eBus website,
saves the rendered HTML and CSV file, and stores the parsed data in a SQLite database.
"""

import re
import pandas as pd
from playwright.sync_api import sync_playwright
from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from shapely.geometry import Point
import folium
from folium.plugins import MarkerCluster


class taipei_route_list:
    """
    Manages fetching, parsing, and storing route data for Taipei eBus.
    """

    def __init__(self, working_directory: str = 'data'):
        """
        Initializes the taipei_route_list, fetches webpage content,
        configures the ORM, and sets up the SQLite database.

        Args:
            working_directory (str): Directory to store the HTML and database files.
        """
        self.working_directory = working_directory
        self.url = 'https://ebus.gov.taipei/ebus?ct=all'
        self.content = None

        # Fetch webpage content
        self._fetch_content()

        # Setup ORM base and table
        Base = declarative_base()

        class bus_route_orm(Base):
            __tablename__ = 'data_route_list'

            route_id = Column(String, primary_key=True)
            route_name = Column(String)
            route_data_updated = Column(Integer, default=0)

        self.orm = bus_route_orm

        # Create and connect to the SQLite engine
        self.engine = create_engine(f'sqlite:///{self.working_directory}/hermes_ebus_taipei.sqlite3')
        self.engine.connect()
        Base.metadata.create_all(self.engine)

        # Create session
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def _fetch_content(self):
        """
        Fetches the webpage content using Playwright and saves it as a local HTML file.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.url)
            page.wait_for_timeout(3000)  # Wait for the page to load
            self.content = page.content()
            browser.close()

        # Save the rendered HTML to a file for inspection
        html_file_path = f'{self.working_directory}/hermes_ebus_taipei_route_list.html'
        with open(html_file_path, "w", encoding="utf-8") as file:
            file.write(self.content)

    def parse_route_list(self) -> pd.DataFrame:
        """
        Parses bus route data from the fetched HTML content.

        Returns:
            pd.DataFrame: DataFrame containing bus route IDs and names.

        Raises:
            ValueError: If no route data is found.
        """
        pattern = r'<li><a href="javascript:go\(\'(.*?)\'\)">(.*?)</a></li>'
        matches = re.findall(pattern, self.content, re.DOTALL)

        if not matches:
            raise ValueError("No data found for route table")

        bus_routes = [(route_id, route_name.strip()) for route_id, route_name in matches]
        self.dataframe = pd.DataFrame(bus_routes, columns=["route_id", "route_name"])
        return self.dataframe

    def save_to_database(self):
        """
        Saves the parsed bus route data to the SQLite database via SQLAlchemy ORM.
        """
        for _, row in self.dataframe.iterrows():
            self.session.merge(self.orm(route_id=row['route_id'], route_name=row['route_name']))

        self.session.commit()

    def read_from_database(self) -> pd.DataFrame:
        """
        Reads bus route data from the SQLite database.

        Returns:
            pd.DataFrame: DataFrame containing bus route data.
        """
        query = self.session.query(self.orm)
        self.db_dataframe = pd.read_sql(query.statement, self.session.bind)
        return self.db_dataframe

    def set_route_data_updated(self, route_id: str, route_data_updated: int = 1):
        """
        Sets the route_data_updated flag in the database.

        Args:
            route_id (str): The ID of the bus route.
            route_data_updated (bool): The value to set for the route_data_updated flag.
        """
        self.session.query(self.orm).filter_by(route_id=route_id).update({"route_data_updated": route_data_updated})
        self.session.commit()


    def set_route_data_unexcepted(self, route_id: str):
        self.session.query(self.orm).filter_by(route_id=route_id).update({"route_data_updated": 2 })
        self.session.commit()

    def __del__(self):
        """
        Closes the session and engine when the object is deleted.
        """
        self.session.close()
        self.engine.dispose()


class taipei_route_info:
    """
    Manages fetching, parsing, and storing bus stop data for a specified route and direction.
    """

    def __init__(self, route_id: str, direction: str = 'go', working_directory: str = 'data'):
        """
        Initializes the taipei_route_info by setting parameters and fetching the webpage content.

        Args:
            route_id (str): The unique identifier of the bus route.
            direction (str): The direction of the route; must be either 'go' or 'come'.
        """
        self.route_id = route_id
        self.direction = direction
        self.content = None
        self.url = f'https://ebus.gov.taipei/Route/StopsOfRoute?routeid={route_id}'
        self.working_directory = working_directory

        if self.direction not in ['go', 'come']:
            raise ValueError("Direction must be 'go' or 'come'")

        self._fetch_content()

    def _fetch_content(self):
        """
        Fetches the webpage content using Playwright and writes the rendered HTML to a local file.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.url)

            if self.direction == 'come':
                page.click('a.stationlist-come-go-gray.stationlist-come')

            page.wait_for_timeout(3000)  # Wait for page render
            self.content = page.content()
            browser.close()

        # Save the rendered HTML to a file for inspection
        self.html_file = f"{self.working_directory}/ebus_taipei_{self.route_id}.html"
        
        # with open(html_file, "w", encoding="utf-8") as file:
        #     file.write(self.content)

    def parse_route_info(self) -> pd.DataFrame:
        """
        Parses the fetched HTML content to extract bus stop data.

        Returns:
            pd.DataFrame: DataFrame containing bus stop information.

        Raises:
            ValueError: If no data is found for the route.
        """
        pattern = re.compile(
            r'<li>.*?<span class="auto-list-stationlist-position.*?">(.*?)</span>\s*'
            r'<span class="auto-list-stationlist-number">\s*(\d+)</span>\s*'
            r'<span class="auto-list-stationlist-place">(.*?)</span>.*?'
            r'<input[^>]+name="item\.UniStopId"[^>]+value="(\d+)"[^>]*>.*?'
            r'<input[^>]+name="item\.Latitude"[^>]+value="([\d\.]+)"[^>]*>.*?'
            r'<input[^>]+name="item\.Longitude"[^>]+value="([\d\.]+)"[^>]*>',
            re.DOTALL
        )

        matches = pattern.findall(self.content)
        if not matches:
            raise ValueError(f"No data found for route ID {self.route_id}")

        bus_routes = [m for m in matches]
        self.dataframe = pd.DataFrame(
            bus_routes,
            columns=["arrival_info", "stop_number", "stop_name", "stop_id", "latitude", "longitude"]
        )

        self.dataframe["direction"] = self.direction
        self.dataframe["route_id"] = self.route_id

        return self.dataframe

    def save_to_database(self):
        """
        Saves the parsed bus stop data to the SQLite database.
        """
        db_file = f"{self.working_directory}/hermes_ebus_taipei.sqlite3"
        engine = create_engine(f"sqlite:///{db_file}")
        Base = declarative_base()

        class bus_stop_orm(Base):
            __tablename__ = "data_route_info_busstop"
            stop_id = Column(Integer)
            arrival_info = Column(String)
            stop_number = Column(Integer, primary_key=True)
            stop_name = Column(String)
            latitude = Column(Float)
            longitude = Column(Float)
            direction = Column(String, primary_key=True)
            route_id = Column(String, primary_key=True)

        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        for _, row in self.dataframe.iterrows():
            session.merge(bus_stop_orm(
                stop_id=row["stop_id"],
                arrival_info=row["arrival_info"],
                stop_number=row["stop_number"],
                stop_name=row["stop_name"],
                latitude=row["latitude"],
                longitude=row["longitude"],
                direction=row["direction"],
                route_id=row["route_id"]
            ))

        session.commit()
        session.close()


def draw_map_with_person_icon(route_id: str, stop_number: int, db_file: str, icon_path: str, output_file: str):
    """
    繪製地圖並在選定站點上繪製小人圖樣。

    Args:
        route_id (str): 公車路線 ID。
        stop_number (int): 站點編號。
        db_file (str): SQLite 資料庫檔案路徑。
        icon_path (str): 小人圖樣的檔案路徑。
        output_file (str): 輸出的地圖檔案路徑。
    """
    # 從資料庫讀取站點資料
    engine = create_engine(f"sqlite:///{db_file}")
    query = f"""
        SELECT stop_number, stop_name, latitude, longitude
        FROM data_route_info_busstop
        WHERE route_id = '{route_id}'
    """
    df = pd.read_sql(query, engine)

    # 檢查是否有資料
    if df.empty:
        print(f"無法找到路線 {route_id} 的站點資料。")
        return

    # 將資料轉換為 GeoDataFrame
    df['geometry'] = df.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

    # 找到選定的站點
    selected_stop = gdf[gdf['stop_number'] == stop_number]
    if selected_stop.empty:
        print(f"無法找到站點編號 {stop_number} 的資料。")
        return

    # 繪製地圖
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf.plot(ax=ax, color='blue', markersize=10, label='所有站點')

    # 繪製選定站點
    selected_stop.plot(ax=ax, color='red', markersize=50, label=f'選定站點: {stop_number}')

    # 在選定站點上繪製小人圖樣
    stop_coords = selected_stop.geometry.iloc[0].coords[0]
    img = OffsetImage(plt.imread(icon_path), zoom=0.1)  # 調整小人圖樣大小
    ab = AnnotationBbox(img, stop_coords, frameon=False)
    ax.add_artist(ab)

    # 設定地圖標題和圖例
    plt.title(f"公車路線 {route_id} 地圖")
    plt.xlabel("經度")
    plt.ylabel("緯度")
    plt.legend()

    # 儲存地圖
    plt.savefig(output_file)
    plt.close()
    print(f"地圖已儲存為 {output_file}")


def is_incoming(arrival_info):
    if pd.isnull(arrival_info):
        return False
    match = re.search(r"(\d+)\s*分鐘", arrival_info)
    if match:
        minutes = int(match.group(1))
        return minutes <= 3
    # 處理其他格式，例如 "即將進站"
    if "即將進站" in arrival_info:
        return True
    return False


def draw_interactive_map(route_id: str, stop_number: int, db_file: str, icon_path: str, bus_icon_path: str, output_file: str):
    """
    使用 folium 繪製互動式地圖，並在選定站點上顯示小人圖樣和三分鐘內即將進站的公車。

    Args:
        route_id (str): 公車路線 ID。
        stop_number (int): 站點編號。
        db_file (str): SQLite 資料庫檔案路徑。
        icon_path (str): 小人圖樣的檔案路徑。
        bus_icon_path (str): 小公車圖樣的檔案路徑。
        output_file (str): 輸出的地圖檔案路徑。
    """
    # 從資料庫讀取站點資料
    engine = create_engine(f"sqlite:///{db_file}")
    query = f"""
        SELECT stop_number, stop_name, latitude, longitude, arrival_info
        FROM data_route_info_busstop
        WHERE route_id = '{route_id}'
    """
    df = pd.read_sql(query, engine)

    # 檢查是否有資料
    if df.empty:
        print(f"無法找到路線 {route_id} 的站點資料。")
        return

    # 初始化地圖，將地圖中心設置為第一個站點的經緯度
    first_stop = df.iloc[0]
    m = folium.Map(location=[first_stop['latitude'], first_stop['longitude']], zoom_start=13)

    # 使用 MarkerCluster 將所有站點標記在地圖上
    marker_cluster = MarkerCluster().add_to(m)
    for _, row in df.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"站名: {row['stop_name']}<br>站序: {row['stop_number']}",
            icon=folium.Icon(color="blue", icon="info-sign"),
        ).add_to(marker_cluster)

    # 找到選定的站點
    selected_stop = df[df['stop_number'] == stop_number]
    if selected_stop.empty:
        print(f"無法找到站點編號 {stop_number} 的資料。")
        return

    # 在選定站點上顯示小人圖樣
    selected_row = selected_stop.iloc[0]
    folium.Marker(
        location=[selected_row['latitude'], selected_row['longitude']],
        popup=f"<b>選定站點</b><br>站名: {selected_row['stop_name']}<br>站序: {selected_row['stop_number']}",
        icon=folium.CustomIcon(icon_path, icon_size=(50, 50)),  # 使用小人圖樣
    ).add_to(m)

    # 篩選出三分鐘內即將進站的站點
    incoming_buses = df[df['arrival_info'].apply(is_incoming)]

    # 調試輸出
    print("即將進站的公車資料：")
    print(incoming_buses)

    # 在地圖上顯示即將進站的公車
    for _, bus in incoming_buses.iterrows():
        folium.Marker(
            location=[bus['latitude'], bus['longitude']],
            popup=f"<b>即將進站公車</b><br>站名: {bus['stop_name']}<br>站序: {bus['stop_number']}<br>到站時間: {bus['arrival_info']}",
            icon=folium.CustomIcon(bus_icon_path, icon_size=(50, 50)),  # 使用小公車圖樣
        ).add_to(m)

    # 將地圖保存為 HTML 檔案
    m.save(output_file)
    print(f"互動式地圖已儲存為 {output_file}")


if __name__ == "__main__":
    # Initialize and process route data
    route_list = taipei_route_list()
    route_list.parse_route_list()
    route_list.save_to_database()

    # 使用者輸入站點編號
    route_id = input("請輸入公車路線 ID (例如 0161000900): ")
    stop_number = int(input("請輸入站點編號 (例如 70): "))

    # 繪製互動式地圖
    db_file = f"{route_list.working_directory}/hermes_ebus_taipei.sqlite3"
    icon_path = "C:/Users/User/Desktop/cycu_oop_11372002/20250429/person_icon.png"  # 小人圖樣檔案
    bus_icon_path = "C:/Users/User/Desktop/cycu_oop_11372002/20250429/bus_icon.png"  # 小公車圖樣檔案
    output_file = f"map_{route_id}_stop_{stop_number}.html"

    draw_interactive_map(route_id, stop_number, db_file, icon_path, bus_icon_path, output_file)

    # 自動打開地圖
    import webbrowser
    webbrowser.open(output_file)

    # Query and print route data
    from sqlalchemy import create_engine
    import pandas as pd

    db_file = "C:/Users/User/Desktop/cycu_oop_11372002/20250429/data/hermes_ebus_taipei.sqlite3"
    engine = create_engine(f"sqlite:///{db_file}")

    query = """
        SELECT stop_number, stop_name, latitude, longitude, arrival_info
        FROM data_route_info_busstop
        WHERE route_id = '0161000900'
    """
    df = pd.read_sql(query, engine)

    print(df[['stop_number', 'stop_name', 'arrival_info']])