import json
from fpdf import FPDF
import os

def test_simple_pdf():
    try:
        # 创建一个简单的PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, "Hello PDF!", ln=True, align='C')
        
        # 保存到文件
        workspace_path = "./stock_analysis_workspace"
        os.makedirs(workspace_path, exist_ok=True)
        file_path = os.path.join(workspace_path, "test_report.pdf")
        pdf.output(file_path)
        
        print(f"✅ 简单PDF已生成: {file_path}")
        print(f"文件大小: {os.path.getsize(file_path)} bytes")
        return True
    except Exception as e:
        print(f"❌ PDF生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_simple_pdf()