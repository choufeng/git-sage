# Git Sage 接入 Gemini 和 ModelScope 实施计划

## 项目概述

本文档详细描述了为 Git Sage 项目添加 Gemini 和 ModelScope 两种AI服务接入的完整实施方案。

## 当前架构分析

### 现有支持的AI服务
- **Ollama**：本地部署的开源大模型服务
- **OpenRouter**：第三方AI模型聚合平台
- **DeepSeek**：深度求索的AI服务

### 现有技术栈
- **配置管理**：YAML配置文件，支持动态切换服务
- **AI框架**：基于 LangChain 的统一接口
- **CLI交互**：使用 Click 和 Inquirer 的交互式命令行

## 目标服务规格

### Gemini API
- **提供商**：Google
- **官方文档**：https://ai.google.dev/docs
- **鉴权方式**：API Key
- **默认端点**：`https://generativelanguage.googleapis.com/v1beta`
- **推荐模型**：`gemini-pro`, `gemini-pro-vision`
- **依赖包**：`langchain-google-genai`, `google-generativeai`

### ModelScope API  
- **提供商**：阿里云/魔搭社区
- **官方文档**：https://www.modelscope.cn/docs
- **鉴权方式**：API Key 或 Access Key/Secret Key
- **默认端点**：`https://dashscope.aliyuncs.com/api/v1`
- **推荐模型**：`qwen-max`, `qwen-plus`, `qwen-turbo`
- **依赖包**：`modelscope`, `dashscope`

## 实施步骤

### 阶段1: 基础设施准备

#### 1.1 更新项目依赖 (`setup.py`)
```python
install_requires=[
    # 现有依赖...
    'langchain-google-genai>=0.1.0',
    'google-generativeai>=0.3.0', 
    'modelscope>=1.10.0',
    'dashscope>=1.0.0',
]
```

#### 1.2 扩展配置管理器 (`git_sage/config/config_manager.py`)
- 新增端点常量：`GEMINI_ENDPOINT`, `MODELSCOPE_ENDPOINT`
- 扩展 `update_config` 方法支持新服务
- 更新默认配置注释

#### 1.3 更新枚举定义 (`git_sage/cli/main.py`)
- 扩展 `ModelService` 枚举
- 更新服务映射字典
- 添加交互式选择选项

### 阶段2: AI处理器集成

#### 2.1 Gemini集成 (`git_sage/core/ai_processor.py`)
```python
elif language_model == "gemini":
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0.5
    )
```

#### 2.2 ModelScope集成
```python
elif language_model == "modelscope":
    return ModelScopeChatModel(
        model=model_name,
        api_key=api_key,
        base_url=endpoint,
        temperature=0.5
    )
```

### 阶段3: 测试与验证

#### 3.1 单元测试
- ConfigManager 新服务配置测试
- AIProcessor 模型创建测试
- CLI 交互流程测试

#### 3.2 集成测试
- 端到端配置-调用-响应流程
- 错误处理和异常情况
- 性能和稳定性测试

#### 3.3 回归测试
- 确保现有功能正常运行
- 配置兼容性测试

### 阶段4: 文档与示例

#### 4.1 用户文档更新
- README.md 新增配置章节
- 中文文档同步更新
- 配置示例和故障排除

#### 4.2 开发文档
- API接入指南
- 扩展新服务的开发文档
- 架构设计文档

## 配置示例

### Gemini 配置示例
```yaml
language: "zh-CN"
language_model: "gemini"
model: "gemini-pro"
endpoint: "https://generativelanguage.googleapis.com/v1beta"
api_key: "YOUR_GEMINI_API_KEY"
```

### ModelScope 配置示例
```yaml
language: "zh-CN" 
language_model: "modelscope"
model: "qwen-max"
endpoint: "https://dashscope.aliyuncs.com/api/v1"
api_key: "YOUR_MODELSCOPE_API_KEY"
```

## 使用指南

### Gemini 配置步骤
1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 创建或登录Google账号
3. 生成API密钥
4. 运行 `gsg set` 选择Gemini服务
5. 输入API密钥和模型名称

### ModelScope 配置步骤
1. 访问 [阿里云灵积平台](https://dashscope.console.aliyun.com/)
2. 注册或登录阿里云账号
3. 开通DashScope服务并获取API-KEY
4. 运行 `gsg set` 选择ModelScope服务
5. 输入API密钥和模型名称

## 质量保证

### 错误处理策略
- API连接超时和重试机制
- 鉴权失败的友好提示
- 模型不存在的错误处理
- 配置无效时的降级方案

### 性能优化
- API调用缓存机制
- 请求参数优化
- 响应时间监控

### 安全性考虑
- API密钥的安全存储
- 敏感信息的脱敏处理
- 网络请求的SSL验证

## 发布计划

### Alpha 版本 (内部测试)
- 基础功能实现
- 核心测试用例通过
- 代码审查完成

### Beta 版本 (用户测试)  
- 完整功能测试
- 用户体验优化
- 文档完善

### 正式版本 (全面发布)
- 所有测试通过
- 文档齐全
- 性能验证完成

## 风险评估与缓解

### 技术风险
- **依赖冲突**：使用锁定版本和虚拟环境测试
- **API变更**：关注官方更新，及时适配
- **性能问题**：性能基准测试和优化

### 用户风险  
- **配置复杂**：提供详细文档和示例
- **成本问题**：说明各服务的计费方式
- **服务稳定性**：提供多服务选择和切换指南

## 成功指标

- 新服务配置成功率 > 95%
- API调用成功率 > 99%
- 用户满意度 > 4.5/5
- 文档完整性 100%
- 测试覆盖率 > 90%

## 维护计划

### 短期维护 (1-3个月)
- 用户反馈收集和问题修复
- 性能监控和优化
- 文档更新和完善

### 长期维护 (3-12个月)
- API版本升级适配
- 新模型支持
- 功能增强和扩展

---

**文档版本**: v1.0  
**创建时间**: 2025-01-08  
**最后更新**: 2025-01-08  
**负责人**: Git Sage 开发团队
