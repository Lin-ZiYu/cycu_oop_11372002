import geopandas as gpd
import matplotlib.pyplot as plt
import os

# 找出 taipei_town 目錄下的第一個 .shp 檔案
shp_dir = "20250520/town"
shp_file = None
for fname in os.listdir(shp_dir):
    if fname.endswith(".shp"):
        shp_file = os.path.join(shp_dir, fname)
        break

if shp_file is None:
    print("No shapefile found in", shp_dir)
else:
    # 讀取 shapefile
    gdf = gpd.read_file(shp_file)
    
    # 篩選出桃園市、臺北市、新北市和基隆市的資料，假設屬性欄位名稱為 "COUNTYNAME"
    target_cities = ["桃園市", "臺北市", "新北市", "基隆市"]
    filtered_gdf = gdf[gdf["COUNTYNAME"].isin(target_cities)]
    
    # 繪製篩選後的地圖
    filtered_gdf.plot(edgecolor='black', figsize=(10, 10))
    plt.title("Selected Cities: Taoyuan, Taipei, New Taipei, Keelung")
    plt.axis('equal')
    plt.show()
