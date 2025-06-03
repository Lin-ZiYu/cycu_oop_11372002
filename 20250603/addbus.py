# -*- coding: utf-8 -*-
"""
This module retrieves bus stop data for a specific route and direction from the Taipei eBus website,
saves the rendered HTML and CSV file, and stores the parsed data in a SQLite database.
"""
import json
import re
import os
import pandas as pd
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


class taipei_route_info:
    """
    Manages fetching, parsing, and storing bus stop data for a specified route and direction.
    """
    def __init__(self, route_id: str, direction: str = 'go', working_directory: str = 'data'):
        self.route_id = route_id
        self.direction = direction
        self.content = None
        self.url = f'https://ebus.gov.taipei/Route/StopsOfRoute?routeid={route_id}'
        self.working_directory = working_directory

        if self.direction not in ['go', 'come']:
            raise ValueError("Direction must be 'go' or 'come'")
        
        self.html_file = f"{self.working_directory}/ebus_taipei_{self.route_id}.html"

        with open(self.html_file, 'r', encoding='utf-8') as file:
            self.content = file.read()

    def parse_wkt_fields(self) -> dict:
        """
        Parses WKT fields from the HTML content by capturing keys like 'wkt', 'wkt0', 'wkt1' and their LINESTRING values.
        """
        wkt_dict = {}
        pattern = r'JSON\.stringify\s*\(\s*(\{[\s\S]*?\})\s*\)'
        match = re.search(pattern, self.content)
        if match:
            json_text = match.group(1)
            json_dict = json.loads(json_text)
            for key in json_dict.keys():
                if key.startswith('wkt'):
                    wkt_dict[key] = json_dict[key]
            return wkt_dict
        else:
            return {}
        

class taipei_route_list:
    """
    Manages fetching, parsing, and storing route data for Taipei eBus.
    """
    def __init__(self, working_directory: str = 'data'):
        self.working_directory = working_directory
        self.url = 'https://ebus.gov.taipei/ebus?ct=all'
        self.content = None

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

        self.html_file_path = f'{self.working_directory}/hermes_ebus_taipei_route_list.html'

    def read_from_database(self) -> pd.DataFrame:
        query = self.session.query(self.orm)
        self.db_dataframe = pd.read_sql(query.statement, self.session.bind)
        return self.db_dataframe


if __name__ == "__main__":
    route_list = taipei_route_list()

    # 確保資料夾存在
    if not os.path.exists(route_list.working_directory):
        os.makedirs(route_list.working_directory)

    # 1️⃣ 匯出 bus route 名稱與代碼為 CSV
    route_df = route_list.read_from_database()[["route_name", "route_id"]]
    route_name_code_csv_path = f"{route_list.working_directory}/route_name_code.csv"
    route_df.to_csv(route_name_code_csv_path, index=False, header=False, encoding='utf-8-sig')
    print(f"✅ Saved route name and code to {route_name_code_csv_path}")

    # 2️⃣（可選）處理每條路線的 wkt（保留原本功能）
    all_routes_df = pd.DataFrame()

    for _, row in route_list.read_from_database().iterrows():
        try:
            print(f"Processing route: {row['route_name']} ({row['route_id']})")
            for direction in ["go", "come"]:
                route_info = taipei_route_info(route_id=row["route_id"], direction=direction)
                dict_wkt = route_info.parse_wkt_fields()

                if not dict_wkt:
                    print(f"No WKT data found for route {row['route_name']} ({row['route_id']}) in direction {direction}")
                    continue

                df = pd.DataFrame(dict_wkt.items(), columns=['wkt_id', 'wkt_string'])
                df['route_id'] = route_info.route_id
                df['route_name'] = row["route_name"]
                df['direction'] = "去程" if direction == "go" else "回程"
                all_routes_df = pd.concat([all_routes_df, df], ignore_index=True)

            print(f"Processed route {row['route_name']}:{row['route_id']}")
        except Exception as e:
            print(f"Error processing route {row['route_name']}: {e}")
            raise

    if all_routes_df.empty:
        print("No WKT data to save.")
    else:
        csv_file_path = f"{route_list.working_directory}/all_routes.csv"
        all_routes_df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')
        print(f"✅ Saved WKT data to {csv_file_path}")
