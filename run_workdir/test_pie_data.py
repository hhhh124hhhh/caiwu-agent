import json

# 测试数据 - 分布数据（用于饼图）
distribution_data = {
    "利润率分布": [
        {"利润率区间": "40%+", "公司数量": 1},
        {"利润率区间": "30-40%", "公司数量": 1},
        {"利润率区间": "20-30%", "公司数量": 1}
    ]
}

print("分布数据:")
print(json.dumps(distribution_data, ensure_ascii=False, indent=2))

# 模拟饼图数据处理逻辑
data = distribution_data
category_data = {}

for key, value in data.items():
    print(f"处理键: {key}, 值: {value}")
    if isinstance(value, (list, dict)) and key not in ['trend', 'trend_data']:
        if isinstance(value, list) and len(value) > 0:
            # 如果是列表，尝试计算其长度或其他聚合值
            category_data[key] = len(value)
            print(f"  列表长度: {len(value)}")
        elif isinstance(value, dict):
            # 如果是字典，尝试计算其大小或其他聚合值
            category_data[key] = len(value)
            print(f"  字典大小: {len(value)}")

print(f"分类数据: {category_data}")

if category_data:
    cat_keys = list(category_data.keys())
    cat_values = list(category_data.values())
    print(f"分类键: {cat_keys}")
    print(f"分类值: {cat_values}")
    
    # 这就是问题所在！我们只计算了列表的长度（都是1），而不是实际的公司数量
    # 应该提取"公司数量"字段的值