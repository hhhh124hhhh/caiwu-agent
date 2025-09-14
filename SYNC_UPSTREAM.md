# 同步上游 Youtu-Agent 更新指南

本文档说明如何将上游 Youtu-Agent 仓库的更新同步到你的项目中。

## 自动同步（推荐）

使用提供的脚本自动同步更新：

```bash
uv run python scripts/update_from_upstream.py
```

## 手动同步步骤

如果你更喜欢手动操作，可以按照以下步骤进行：

### 1. 获取上游更新
```bash
git fetch upstream
```

### 2. 合并上游更改
```bash
git merge upstream/main
```

如果出现冲突，需要手动解决冲突后再提交。

### 3. 推送到你的仓库
```bash
git push origin main
```

## 检查远程仓库配置

确认你的远程仓库配置正确：

```bash
git remote -v
```

应该显示类似以下的输出：
```
origin    https://github.com/hhhh124hhhh/caiwu-agent.git (fetch)
origin    https://github.com/hhhh124hhhh/caiwu-agent.git (push)
upstream  https://github.com/TencentCloudADP/youtu-agent.git (fetch)
upstream  https://github.com/TencentCloudADP/youtu-agent.git (push)
```

## 注意事项

1. **冲突处理**：如果上游更改与你的本地更改冲突，Git 会提示你手动解决冲突。
2. **备份**：在执行重大更新前，建议创建备份分支。
3. **测试**：更新后建议运行测试确保功能正常：
   ```bash
   uv run python run_tests.py
   ```

## 创建备份分支

在执行更新前创建备份分支：

```bash
git checkout -b backup-before-update-$(date +%Y%m%d)
git checkout main  # 回到主分支
```