import pandas as pd
import matplotlib.pyplot as plt

def read_and_sum_excel(file_path):
    try:
        # 讀取 Excel 檔案
        df = pd.read_excel(file_path)
        
        # 確認欄位名稱
        if 'x' in df.columns and 'y' in df.columns:
            # 計算 x 和 y 的和
            df['sum'] = df['x'] + df['y']
            
            # 印出結果
            for index, row in df.iterrows():
                print(f"Row {index + 1}: x = {row['x']}, y = {row['y']}, sum = {row['sum']}")
            
            # 繪製散佈圖
            plt.scatter(df['x'], df['y'])
            plt.xlabel('x')
            plt.ylabel('y')
            plt.title('Scatter Plot of x and y')
            plt.show()
        else:
            print("Excel 檔案中沒有找到 'x' 或 'y' 欄位")
    except Exception as e:
        print(f"讀取 Excel 檔案時發生錯誤: {e}")

if __name__ == "__main__":
    # 替換成你的 Excel 檔案路徑
    excel_file_path = '311.xlsx'
    read_and_sum_excel(excel_file_path)