# Changelog

## v1.0.2 - 2025-09-15
- 🐛 修复图表保存路径问题：更新tabular_data_toolkit中generate_charts函数的默认输出目录
- 🛠️ 优化工具配置：将图表默认保存路径从"./run_workdir/sxjg_charts"修改为"./run_workdir"

## v1.0.1 - 2025-09-15
- 🐛 修复报告生成问题：修复ReportAgent无法正确调用save_text_report工具的问题
- 🛠️ 优化工具配置：更新financial_analysis工具包配置，添加generate_text_report和save_text_report工具
- 📝 完善文档：更新CHANGELOG.md记录修复内容

## v1.0.0 - 2025-09-15
- 🚀 发布财务分析智能体(Youtu-Agent) - 专为A股市场设计的智能财务分析系统
- 📊 核心特性：零代码生成错误、显著降低成本、完整分析能力
- 🛠️ 新增标准化工具库：AKShare数据获取工具、财务分析工具包、增强代码执行器
- 🤖 新增智能Agent分工：数据获取→分析计算→结果解读的完整流程
- 💾 新增智能缓存机制：避免重复数据获取，自动检测新财报
- 📈 新增完整分析能力：财务比率计算、趋势分析、健康评估、自动报告生成
- 🎯 解决传统AI财务分析痛点：高错误率、高Token消耗、结果不一致

## frontend/v0.1.5 - 2025-08-29
- add the `utu_agent_ui` package by @fpg2012

- add `exp_analysis` frontend by @qiuchaofan
- add `CONTRIBUTING.md` by @Lightblues
- add detailed quickstart doc by @pakchoi-i
- add Docker support by @YZ-Cai