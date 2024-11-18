# Git Sage

Git Sage 是一个AI驱动的Git助手，它可以帮助你生成更好的提交信息。

## 功能特点

- 自动分析已暂存的更改
- 使用AI生成规范的提交信息
- 支持中英文提交信息
- 支持自定义AI模型配置
- 简单易用的命令行界面

## 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/git-sage.git

# 进入项目目录
cd git-sage

# 安装
pip install -e .

# 运行初始配置向导
gsg-setup
```

## 配置

有多种方式可以配置Git Sage：

1. 运行初始配置向导：
```bash
gsg-setup
```

2. 使用交互式配置：
```bash
gsg config -i
```

3. 单独设置配置项：
```bash
# 查看当前配置
gsg config

# 设置语言（支持 en/zh）
gsg config --language zh

# 设置AI模型
gsg config --model ollama

# 设置API密钥
gsg config --api-key your-key

# 设置模型服务地址
gsg config --endpoint http://localhost:11434
```

## 使用方法

生成提交信息：

```bash
# 首先使用git add暂存你的更改
git add .

# 然后使用gsg生成提交信息并提交
gsg a
```

## 提交信息规范

提交信息遵循 Conventional Commit 规范，格式如下：

```
{标签}: 变更的主题或标题
可选的详细描述
```

### 提交标签说明

#### 补丁版本 (PATCH)
以下标签会产生补丁版本更新：

- `Fix`: 用于修复bug
- `Build`: 仅构建过程的变更
- `Maint`/`Maintenance`: 小型维护任务，如技术债务清理、重构、构建过程变更和非破坏性依赖更新
- `Test`: 用于应用程序端到端测试
- `Patch`: 当其他补丁标签不适用时使用的通用补丁标签

#### 次要版本 (MINOR)
以下标签会产生次要版本更新：

- `Feat`/`Feature`/`New`: 实现新功能
- `Minor`: 当其他次要版本标签不适用时使用的通用标签
- `Update`: 对现有功能的向后兼容增强

#### 主要版本 (MAJOR)
以下标签会产生主要版本更新：

- `Breaking`: 用于向后不兼容的增强或功能
- `Major`: 当其他主要版本标签不适用时使用的通用标签

#### 无版本更新 (NO-OP)
以下标签不会触发版本更新：

- `Docs`: 仅文档变更
- `Chore`: 用于其他不会影响实际环境的变更，如代码注释、非包或应用程序文件的变更、单元测试等

## 配置说明

配置文件位于 `~/.git-sage/config.yml`，包含以下配置项：

- language: 提交信息语言 (默认为 en)
- language_model: 选择使用的语言模型服务 (默认为 ollama)
- model: 选择具体的模型名称 (默认为 codellama)
- endpoint: 模型服务地址 (默认为 http://localhost:11434)
- api_key: API密钥 (默认为 ollama)

所有配置项都可以通过 `gsg config --<配置项> <值>` 来修改，或使用交互式配置 `gsg config -i`。

## 依赖项

- Python >= 3.8
- langgraph >= 0.2.50
- gitpython >= 3.1.40
- click >= 8.1.7
- pyyaml >= 6.0.1

## 许可证

MIT License
