import re
import os

class HTMLCleanerTest:
    """
    测试HTML清理逻辑，专注于表格单元格内嵌套标签的处理
    """
    
    def _clean_html_for_pdf(self, html_content: str) -> str:
        """
        清理HTML内容以适配PDF渲染，特别处理表格单元格内的嵌套标签
        
        Args:
            html_content: 原始HTML内容
            
        Returns:
            str: 清理后的HTML内容
        """
        # 移除emoji字符
        html_content = re.sub(r'[\U00010000-\U0010FFFF]', '', html_content)
        
        # 修复HTML结构问题
        html_content = re.sub(r'<head[^>]*>(.*?)</head>', r'<head>\1</head>', html_content, flags=re.DOTALL)
        
        # 移除可能导致问题的CSS和JavaScript
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
        
        # 简化HTML结构
        html_content = re.sub(r'<meta[^>]*>', '', html_content)
        
        # 处理表格单元格内的嵌套HTML标签问题
        # 这是修复"Unsupported nested HTML tags inside <td> element: <h2>"错误的关键部分
        # 提取所有<td>标签内容，处理内部的嵌套标签
        def process_table_cells(match):
            td_content = match.group(1)
            # 将<td>内的标题标签(h1-h6)转换为加粗文本
            td_content = re.sub(r'<h([1-6])[^>]*>(.*?)</h\1>', r'<strong>\2</strong>', td_content)
            # 处理其他可能导致问题的嵌套标签
            td_content = re.sub(r'<div[^>]*>(.*?)</div>', r'\1', td_content)
            td_content = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', td_content)
            # 移除可能存在的样式属性
            td_content = re.sub(r'<([a-z][a-z0-9]*)[^>]*style=["\'][^"\']*["\'][^>]*>', r'<\1>', td_content)
            return f'<td>{td_content}</td>'
        
        # 应用表格单元格处理
        html_content = re.sub(r'<td[^>]*>(.*?)</td>', process_table_cells, html_content, flags=re.DOTALL)
        
        # 确保基本的HTML结构
        if not html_content.strip().startswith('<!DOCTYPE') and not html_content.strip().startswith('<html'):
            html_content = f'<html><head><meta charset="UTF-8"></head><body>{html_content}</body></html>'
        
        return html_content

def test_nested_html_in_td_fix():
    """
    测试修复后的HTML清理逻辑，验证表格单元格内嵌套HTML标签的处理
    """
    print("测试表格单元格内嵌套HTML标签的清理逻辑...")
    
    # 创建测试HTML内容，包含嵌套在<td>内的<h2>标签（这是之前失败的场景）
    test_html = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>嵌套HTML标签测试报告</title>
    </head>
    <body>
        <h1>嵌套HTML标签测试报告</h1>
        
        <h2>测试表格 - 包含嵌套标签</h2>
        <table border="1">
            <tr>
                <th>公司名称</th>
                <th>财务指标</th>
                <th>趋势分析</th>
            </tr>
            <tr>
                <td>陕西建工</td>
                <td>营业收入</td>
                <td><h2>下降趋势 -62.03%</h2></td>
            </tr>
            <tr>
                <td>陕西建工</td>
                <td>净利润</td>
                <td><h3>大幅下滑 -69.43%</h3></td>
            </tr>
            <tr>
                <td>测试公司</td>
                <td>ROE</td>
                <td><div><span style="color: red;">负面信号</span></div></td>
            </tr>
        </table>
        
        <h2>普通内容区域</h2>
        <p>这是一个正常的段落，不包含在表格内。</p>
        <p>分析日期: 2024-01-01</p>
    </body>
    </html>
    """
    
    # 创建清理器实例
    cleaner = HTMLCleanerTest()
    
    try:
        # 调用HTML清理方法
        print("\n正在清理包含嵌套HTML标签的表格...")
        cleaned_html = cleaner._clean_html_for_pdf(test_html)
        
        # 验证清理结果
        print("\n验证清理结果:")
        
        # 检查是否移除了td内的h2标签
        if '<td><h2>' not in cleaned_html and '<td><h3>' not in cleaned_html:
            print("✅ 成功移除表格单元格内的标题标签")
        else:
            print("❌ 未能移除表格单元格内的标题标签")
            return False
        
        # 检查是否保留了内容并转换为加粗
        if '<td><strong>下降趋势 -62.03%</strong></td>' in cleaned_html and \
           '<td><strong>大幅下滑 -69.43%</strong></td>' in cleaned_html:
            print("✅ 成功将标题标签内容转换为加粗文本")
        else:
            print("❌ 未能正确转换标题标签内容")
            return False
        
        # 检查是否处理了嵌套的div和span标签
        if '<td>负面信号</td>' in cleaned_html or '<td><strong>负面信号</strong></td>' in cleaned_html:
            print("✅ 成功处理表格单元格内的嵌套div和span标签")
        else:
            print("❌ 未能正确处理嵌套的div和span标签")
            return False
        
        # 检查表格外的标题标签是否保持不变
        if '<h1>嵌套HTML标签测试报告</h1>' in cleaned_html and '<h2>测试表格 - 包含嵌套标签</h2>' in cleaned_html:
            print("✅ 表格外的标题标签保持不变")
        else:
            print("❌ 表格外的标题标签被错误修改")
            return False
        
        print("\n✅ 所有测试通过! 清理逻辑能够正确处理表格单元格内的嵌套HTML标签。")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {str(e)}")
        return False

if __name__ == "__main__":
    # 运行测试
    success = test_nested_html_in_td_fix()
    
    # 退出码反映测试结果
    exit(0 if success else 1)