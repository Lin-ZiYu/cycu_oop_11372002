
def print_right(text):
    # 計算需要的前置空格數量
    leading_spaces = 40 - len(text)
    # 使用空格重複運算符號 * 來生成前置空格
    result = ' ' * leading_spaces + text
    # 列印結果
    print(result)

# 測試範例
print_right("Monty")
print_right("Python's")
print_right("Flying Circus")