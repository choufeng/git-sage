# PR 编辑功能使用指南

## 概述
现在 `gsg pr` 命令支持中途编辑功能，类似于 `gsg c` 命令。用户可以在AI生成PR内容后，对PR标题和描述进行编辑，然后再创建Pull Request。

## 新功能特点

### 1. 默认编辑模式
当运行 `gsg pr` 时，系统会：
1. 分析分支变更并生成PR内容
2. **自动打开编辑器让你编辑PR标题和描述**
3. 显示编辑后的PR信息
4. 询问是否创建PR

### 2. 跳过编辑模式
使用 `--no-edit` 选项可以跳过编辑步骤：
```bash
gsg pr --no-edit
```

### 3. 仅查看模式
使用 `--dry-run` 选项可以仅查看生成的PR信息，不进行编辑也不创建PR：
```bash
gsg pr --dry-run
```

## 使用方法

### 基本用法（包含编辑）
```bash
gsg pr
```
系统会：
1. 生成AI建议的PR内容
2. 打开编辑器（vim/你的默认编辑器）
3. 让你编辑PR标题和描述
4. 保存退出后继续创建流程

### 编辑器格式说明
编辑器会显示如下简洁格式：
```markdown
# PR Title
这里是AI生成的PR标题

# PR Description
### Description
这里是AI生成的PR描述内容
- 包含各种技术细节

### Related issues or context
- 相关链接和上下文

### QA
[QA: None/Verify] - QA说明
```

### 编辑规则
- 在 `# PR Title` 下面编辑标题（只取第一行非空内容）
- 在 `# PR Description` 下面编辑描述内容
- **只有** `# PR Title` 和 `# PR Description` 会被识别为特殊标记
- **所有其他内容都会被保留**，包括 `### Description`、`### QA`、`#` 注释等
- 如果标题为空，操作会被取消
- **建议**：删除不需要的注释行以保持PR清洁

### 快速创建（跳过编辑）
```bash
gsg pr --no-edit
```

### 仅查看内容
```bash
gsg pr --dry-run
```

## 编辑器设置
系统会使用环境变量 `EDITOR` 指定的编辑器，如果未设置则默认使用 `vim`。

设置你喜欢的编辑器：
```bash
export EDITOR=code  # VS Code
export EDITOR=nano  # Nano
export EDITOR=vim   # Vim（默认）
```

## 示例工作流程

1. 在功能分支上完成开发
2. 运行 `gsg pr`
3. 系统分析变更并生成PR内容
4. 编辑器自动打开，显示生成的内容
5. 根据需要编辑标题和描述
6. 保存并退出编辑器
7. 系统显示编辑后的PR信息
8. 确认创建PR

## 与 gsg c 的对比
- `gsg c`：编辑commit消息
- `gsg pr`：编辑PR标题和描述
- 两者都支持中途编辑功能
- 两者都支持跳过编辑的选项（commit使用 `confirm=False`，PR使用 `--no-edit`）

## 注意事项
- 编辑功能仅在非 `--dry-run` 模式下工作
- 如果PR标题为空，操作会被取消
- 临时编辑文件会在编辑完成后自动清理