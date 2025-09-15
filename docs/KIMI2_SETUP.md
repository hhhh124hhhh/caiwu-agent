# Kimi2 模型配置指南

本文档说明如何在 youtu-agent 项目中配置和使用 Kimi2 模型。

## 配置步骤

1. **获取 Moonshot API 密钥**
   - 访问 [Moonshot AI 平台](https://platform.moonshot.ai/) 注册账户
   - 在账户设置中获取 API 密钥

2. **设置环境变量**
   ```bash
   # Windows (Command Prompt)
   set MOONSHOT_API_KEY=your_actual_api_key_here
   
   # Windows (PowerShell)
   $env:MOONSHOT_API_KEY="your_actual_api_key_here"
   
   # Linux/macOS
   export MOONSHOT_API_KEY=your_actual_api_key_here
   ```

3. **使用 Kimi2 模型运行代理**
   ```bash
   # 使用 Kimi2 配置运行 CLI 聊天
   python scripts/cli_chat.py --config_name kimi2_agent --stream
   ```

## 配置文件说明

- [configs/model/kimi2.yaml](file:///d:/youtu-agent/configs/model/kimi2.yaml): Kimi2 模型配置文件
- [configs/agents/kimi2_agent.yaml](file:///d:/youtu-agent/configs/agents/kimi2_agent.yaml): 使用 Kimi2 模型的代理配置
- [.env](file:///d:/youtu-agent/.env): 环境变量配置文件

## 测试配置

可以使用以下脚本测试 Kimi2 模型连接：
```bash
python test_kimi2.py
```

## 故障排除

如果遇到连接问题，请检查：
1. API 密钥是否正确设置
2. 网络连接是否正常
3. 是否能够访问 https://api.moonshot.cn/v1