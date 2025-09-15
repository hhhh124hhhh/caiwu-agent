# GitHub 同步操作指南

本指南将帮助您将本地的财务分析项目同步到您的GitHub账户。

## 步骤1：在GitHub上创建新仓库

1. 访问 https://github.com 并登录您的账户
2. 点击右上角的 "+" 图标，选择 "New repository"
3. 设置仓库名称为 `chinese-stock-analysis-toolkit`
4. 添加描述："A specialized toolkit for Chinese A-share financial data analysis with smart caching and standardized analysis capabilities"
5. 选择 Public（或 Private 如果您希望私有）
6. **重要**：不要初始化 README
7. 点击 "Create repository"

## 步骤2：获取仓库URL

创建仓库后，您会看到一个页面，显示类似以下的命令：
```bash
git remote add origin https://github.com/YOUR_USERNAME/chinese-stock-analysis-toolkit.git
```

## 步骤3：配置本地仓库的远程地址

1. 打开命令提示符或终端
2. 进入项目目录：
   ```bash
   cd d:\youtu-agent\financial_analysis_project
   ```

3. 添加远程仓库地址（将 `YOUR_USERNAME` 替换为您的GitHub用户名）：
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/chinese-stock-analysis-toolkit.git
   ```

## 步骤4：推送代码到GitHub

执行以下命令推送所有代码到GitHub：
```bash
git push -u origin master
```

## 如果您启用了双因素认证（2FA）

如果您启用了双因素认证，需要创建个人访问令牌：

1. 访问 GitHub Settings
2. 点击 "Developer settings"
3. 点击 "Personal access tokens"
4. 点击 "Tokens (classic)"
5. 点击 "Generate new token (classic)"
6. 给它起个名字，如 "financial-analysis-toolkit"
7. 选择作用域：`repo`
8. 点击 "Generate token"
9. 复制令牌并安全保存

当推送时提示输入密码时，输入您的个人访问令牌而不是密码。

## 验证同步

推送完成后，您可以在以下URL查看您的代码：
```
https://github.com/YOUR_USERNAME/chinese-stock-analysis-toolkit
```

## 后续更新

如果您对本地代码进行了修改并希望推送到GitHub：

1. 添加更改的文件：
   ```bash
   git add .
   ```

2. 提交更改：
   ```bash
   git commit -m "描述您的更改"
   ```

3. 推送到GitHub：
   ```bash
   git push
   ```