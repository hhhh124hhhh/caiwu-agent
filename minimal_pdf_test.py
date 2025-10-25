from fpdf import FPDF
import os

# 创建输出目录
os.makedirs("./minimal_test_output", exist_ok=True)

# 创建PDF文档
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(0, 10, "Hello World!", ln=True)

# 保存PDF文件
file_path = "./minimal_test_output/test.pdf"
pdf.output(file_path)

print(f"PDF已生成: {file_path}")
print(f"文件存在: {os.path.exists(file_path)}")