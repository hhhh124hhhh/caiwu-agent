import json
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 直接复制需要的函数来测试
def _format_industry_analysis_as_markdown(data: dict) -> str:
    """
    将行业分析数据格式化为Markdown报告
    
    Args:
        data: 包含行业分析数据的字典
        
    Returns:
        str: 格式化后的Markdown报告内容
    """
    try:
        # 获取行业分析数据
        industry_data = data.get("医药行业分析", {})
        key_findings = data.get("关键发现", {})
        
        # 获取基本信息
        analysis_time = industry_data.get("分析时间", "未知时间")
        company_count = industry_data.get("分析公司数量", 0)
        companies = industry_data.get("公司明细", [])
        
        # 生成报告标题和基本信息
        report_content = []
        report_content.append("# 医药行业财务分析报告")
        report_content.append("=" * 18)
        report_content.append(f"**分析时间**: {analysis_time}")
        report_content.append(f"**分析公司数量**: {company_count}")
        report_content.append(f"**报告日期**: {datetime.now().strftime('%Y-%m-%d')}")
        report_content.append("")
        
        # 添加公司明细表
        if companies and isinstance(companies, list):
            report_content.append("## 公司明细")
            report_content.append("")
            report_content.append("| 公司名称 | 股票代码 | 营收(亿元) | 净利润(亿元) | 净利润率(%) | ROE(%) | 资产负债率(%) | 行业分类 |")
            report_content.append("|---------|---------|----------|------------|------------|--------|-------------|---------|")
            
            for company in companies:
                if isinstance(company, dict):
                    name = company.get("名称", "")
                    code = company.get("股票代码", "")
                    revenue = company.get("营收(亿元)", 0)
                    net_profit = company.get("净利润(亿元)", 0)
                    net_profit_margin = company.get("净利润率", 0)
                    roe = company.get("ROE", 0)
                    debt_ratio = company.get("资产负债率", 0)
                    category = company.get("行业分类", "")
                    
                    # 格式化数值
                    revenue_str = f"{revenue:.2f}" if isinstance(revenue, (int, float)) else str(revenue)
                    net_profit_str = f"{net_profit:.2f}" if isinstance(net_profit, (int, float)) else str(net_profit)
                    net_profit_margin_str = f"{net_profit_margin:.2f}" if isinstance(net_profit_margin, (int, float)) else str(net_profit_margin)
                    roe_str = f"{roe:.2f}" if isinstance(roe, (int, float)) else str(roe)
                    debt_ratio_str = f"{debt_ratio:.2f}" if isinstance(debt_ratio, (int, float)) else str(debt_ratio)
                    
                    report_content.append(f"| {name} | {code} | {revenue_str} | {net_profit_str} | {net_profit_margin_str} | {roe_str} | {debt_ratio_str} | {category} |")
            report_content.append("")
        
        # 添加关键发现
        if key_findings and isinstance(key_findings, dict):
            report_content.append("## 关键发现")
            report_content.append("")
            for key, value in key_findings.items():
                # 将键名转换为更易读的中文
                readable_key = _translate_key_findings_key(key)
                report_content.append(f"- **{readable_key}**: {value}")
            report_content.append("")
        
        return "\n".join(report_content)
    except Exception as e:
        # 如果解析失败，返回错误信息
        return f"# 行业分析报告格式化错误\n\n{str(e)}"

def _translate_key_findings_key(key: str) -> str:
    """
    将关键发现的键名翻译为更易读的中文
    """
    translations = {
        "利润率超过10%的公司数量": "利润率超过10%的公司数量",
        "平均净利润率": "平均净利润率",
        "最高利润率": "最高利润率",
        "最低利润率": "最低利润率",
        "行业特点": "行业特点"
    }
    return translations.get(key, key)

# 测试数据 - 医药行业分析数据
medical_data = {
    "医药行业分析": {
        "分析时间": "2025年",
        "分析公司数量": 5,
        "公司明细": [
            {
                "名称": "药明康德",
                "股票代码": "603259",
                "净利润率": 41.64,
                "营收(亿元)": 207.99,
                "净利润(亿元)": 86.60,
                "ROE": 14.17,
                "资产负债率": 27.93,
                "行业分类": "CXO"
            },
            {
                "名称": "迈瑞医疗",
                "股票代码": "300760",
                "净利润率": 31.25,
                "营收(亿元)": 167.43,
                "净利润(亿元)": 52.33,
                "ROE": 11.51,
                "资产负债率": 25.10,
                "行业分类": "医疗器械"
            },
            {
                "名称": "恒瑞医药",
                "股票代码": "600276",
                "净利润率": 28.26,
                "营收(亿元)": 157.61,
                "净利润(亿元)": 44.55,
                "ROE": 7.54,
                "资产负债率": 6.14,
                "行业分类": "创新药"
            },
            {
                "名称": "片仔癀",
                "股票代码": "600436",
                "净利润率": 26.92,
                "营收(亿元)": 53.79,
                "净利润(亿元)": 14.48,
                "ROE": 9.49,
                "资产负债率": 18.77,
                "行业分类": "中药"
            },
            {
                "名称": "云南白药",
                "股票代码": "000538",
                "净利润率": 17.15,
                "营收(亿元)": 212.57,
                "净利润(亿元)": 36.45,
                "ROE": 8.97,
                "资产负债率": 25.73,
                "行业分类": "中药"
            }
        ]
    },
    "关键发现": {
        "利润率超过10%的公司数量": 5,
        "平均净利润率": 29.0,
        "最高利润率": 41.64,
        "最低利润率": 17.15,
        "行业特点": "高利润率、高ROE、相对低负债"
    }
}

# 测试格式化函数
print("测试格式化行业分析数据为Markdown...")
try:
    result = _format_industry_analysis_as_markdown(medical_data)
    print("格式化成功!")
    print("结果预览:")
    print(result[:500] + "..." if len(result) > 500 else result)
except Exception as e:
    print(f"格式化失败: {e}")

# 测试保存报告功能
print("\n测试保存行业分析报告...")
print("此功能需要在完整的项目环境中测试，这里仅测试格式化功能。")