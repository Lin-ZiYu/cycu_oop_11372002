import pandas as pd
import matplotlib.pyplot as plt

# 設置 matplotlib 的後端為 'Agg'
plt.switch_backend('Agg')

# pip install pandas
# pip install matplotlib

# 讀取 CSV 檔案
df = pd.read_csv('ExchangeRate@202503251832.csv')

# 假設欄位名稱為 '資料日期' 和 '現金'
# 確認 '資料日期' 欄位是日期型別
df['資料日期'] = pd.to_datetime(df['資料日期'], errors='coerce')

# 確認 '現金' 欄位是數值型別
df['現金'] = pd.to_numeric(df['現金'], errors='coerce')

# 印出 '現金' 欄位
print(df['現金'])

# 繪製散佈圖
plt.scatter(df['資料日期'], df['現金'])
plt.xlabel('資料日期')
plt.ylabel('現金')
plt.title('Scatter plot of 資料日期 and 現金')

# 保存圖表為檔案
plt.savefig('scatter_plot.png')