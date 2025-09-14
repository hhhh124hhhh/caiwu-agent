# Executed at: 20250913_212413
# Work directory: ./test_workdir4
#==================================================

print("你好，世界！")
中文变量 = "这是一个测试"
print(f"中文测试: {中文变量}")

# Create a file with Chinese content
with open("中文测试文件.txt", "w", encoding="utf-8") as f:
    f.write("这是用Python创建的中文文件内容。")
print("已创建中文测试文件")