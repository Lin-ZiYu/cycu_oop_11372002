import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import lognorm

def plot_lognormal_cdf(mu, sigma, x_points=None, filename='lognormal_cdf.jpg'):
    """
    繪製對數常態累積分布函數 (CDF) 並儲存為 JPG 檔案。

    參數:
    - mu: 對數常態分布的 μ
    - sigma: 對數常態分布的 σ
    - x_points: 自定義的 x 軸點 (若為 None，則使用預設範圍)
    - filename: 儲存的 JPG 檔案名稱 (預設為 'lognormal_cdf.jpg')
    """
    # 計算對數常態分布的參數
    s = sigma
    scale = np.exp(mu)

    # 如果未提供 x_points，使用預設範圍
    if x_points is None:
        x_points = np.linspace(0.01, 10, 500)

    # 計算累積分布函數 (CDF)
    cdf = lognorm.cdf(x_points, s, scale=scale)

    # 繪製圖形
    plt.figure(figsize=(8, 6))
    plt.plot(x_points, cdf, label=f'Lognormal CDF (μ={mu}, σ={sigma})', color='blue')
    plt.title('Lognormal Cumulative Distribution Function')
    plt.xlabel('x')
    plt.ylabel('CDF')
    plt.legend()
    plt.grid()

    # 儲存為 JPG 檔案
    plt.savefig(filename, format='jpg')
    plt.show()

# 主程式：讓使用者輸入 μ 和 σ
if __name__ == "__main__":
    try:
        # 輸入 μ 和 σ
        mu = float(input("請輸入 μ (對數常態分布的平均值): "))
        sigma = float(input("請輸入 σ (對數常態分布的標準差): "))

        # 檢查 σ 是否為正數
        if sigma <= 0:
            raise ValueError("σ 必須為正數！")

        # 呼叫函數繪製圖形
        filename = f"lognormal_cdf_mu{mu}_sigma{sigma}.jpg"
        plot_lognormal_cdf(mu, sigma, filename=filename)
        print(f"圖形已儲存為 {filename}")

    except ValueError as e:
        print(f"輸入錯誤: {e}")
    except Exception as e:
        print(f"發生錯誤: {e}")