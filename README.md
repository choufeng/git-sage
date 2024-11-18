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
```

## 使用方法

1. 配置

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

2. 生成提交信息

```bash
# 首先使用git add暂存你的更改
git add .

# 然后使用gsg生成提交信息并提交
gsg a
```

## 配置说明

配置文件位于 `~/.git-sage/config.yml`，包含以下配置项：

- language: 提交信息语言 (默认为 en)
- language_model: 选择使用的语言模型服务 (默认为 ollama)
- model: 选择具体的模型名称 (默认为 codellama)
- endpoint: 模型服务地址 (默认为 http://localhost:11434)
- api_key: API密钥 (默认为 ollama)

所有配置项都可以通过 `gsg config --<配置项> <值>` 来修改。

## 依赖项

- Python >= 3.8
- langgraph >= 0.2.50
- gitpython >= 3.1.40
- click >= 8.1.7
- pyyaml >= 6.0.1

## 许可证

MIT License
