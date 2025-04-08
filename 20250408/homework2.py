from datetime import datetime, timedelta

def calculate_julian_date(input_time):
    """
    計算輸入時間的星期幾，並計算該時刻至今經過的太陽日數 (Julian date)。

    參數:
    - input_time: 字串格式的時間 (格式為 'YYYY-MM-DD HH:MM')

    回傳:
    - weekday: 該天是星期幾 (例如: 'Monday', 'Tuesday')
    - julian_days: 從輸入時間到現在經過的太陽日數 (以浮點數表示)
    """
    try:
        # 將輸入的時間字串轉換為 datetime 物件
        input_datetime = datetime.strptime(input_time, "%Y-%m-%d %H:%M")
        
        # 計算該天是星期幾
        weekday = input_datetime.strftime("%A")  # 例如: 'Monday', 'Tuesday'
        
        # 計算 Julian date 的基準時間 (公元前 4713 年 1 月 1 日)
        julian_base = datetime(4713, 1, 1, 12) - timedelta(days=1)  # Julian 起始點
        
        # 計算輸入時間的 Julian date
        julian_date_input = (input_datetime - julian_base).total_seconds() / 86400.0
        
        # 計算現在的 Julian date
        now = datetime.now()  # 使用本地時間
        julian_date_now = (now - julian_base).total_seconds() / 86400.0
        
        # 計算從輸入時間到現在經過的太陽日數
        julian_days = julian_date_now - julian_date_input
        
        return weekday, julian_days

    except ValueError:
        raise ValueError("輸入的時間格式不正確，請使用 'YYYY-MM-DD HH:MM' 格式。")

# 範例使用
if __name__ == "__main__":
    try:
        # 輸入時間
        input_time = input("請輸入時間 (格式為 'YYYY-MM-DD HH:MM'): ")
        
        # 呼叫函數計算
        weekday, julian_days = calculate_julian_date(input_time)
        
        # 輸出結果
        print(f"該天是: {weekday}")
        print(f"從該時刻至今經過的太陽日數: {julian_days:.6f}")
    except Exception as e:
        print(f"發生錯誤: {e}")