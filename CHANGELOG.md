# CHANGELOG


## v0.1.2 (2024-11-25)

### Bug Fixes

- Corrected response format in ai_processor.py
  ([`4977206`](https://github.com/choufeng/git-sage/commit/49772064f2ac32aedab07b387d693b55ed8542c5))

- Fixed the response format to match the specified requirements. - Ensured that all text in the
  response is in the specified language.


## v0.1.1 (2024-11-21)

### Bug Fixes

- Update model configuration and improve body formatting
  ([`9edfe8a`](https://github.com/choufeng/git-sage/commit/9edfe8a72b51a80d80de16f1e0d2613f7667b74c))

2. Improved the formatting of the body part in the `AIProcessor` class within `ai_processor.py`.
  Specifically, it ensures that list items are properly formatted with consistent newlines before
  and after them. These changes improve user experience by providing up-to-date information about
  available models and enhance code readability by standardizing the formatting of the body text.
  ```

### Chores

- **release**: 0.1.1 [skip ci]
  ([`372220f`](https://github.com/choufeng/git-sage/commit/372220ff612d15404a991a9017ab17c073d9e6ee))


## v0.1.0 (2024-11-19)

### Bug Fixes

- Add default temperature parameter to AIProcessor initialization
  ([`c6453ad`](https://github.com/choufeng/git-sage/commit/c6453adafe51094656adbb61d9b5973a152532a3))

This commit addresses an issue where the `AIProcessor` class lacked a default value for the
  `temperature` parameter when creating instances of `OllamaLLM` and `ChatOpenAI`. By adding this
  default value, we ensure that all language model instances have a consistent behavior regarding
  temperature control, which can affect the randomness and creativity of generated text. This change
  is non-breaking as it only adds an optional parameter with a default value.

- Refactor AIProcessor prompt generation
  ([`ea3ae1f`](https://github.com/choufeng/git-sage/commit/ea3ae1ff9547b75d0a1823870a6dff321a6bbcec))

Improved the `prompt` generation within the `AIProcessor` class by adding a separate system
  instruction for language specification. This change ensures that all text, including commit
  messages, adheres to the specified language requirements. The changes also streamline the commit
  message format and enhance readability.

- Update README.md to correct language support and minor adjustments
  ([`8dea672`](https://github.com/choufeng/git-sage/commit/8dea6724a3c8fff99c630112ea51dded217792c1))

Corrected the language support description from "多语言提交信息（包括但不限于中文、英文、日文等）" to "中英文提交信息". Also,
  slightly adjusted some phrasing for clarity.

- 提供编辑提交信息的功能
  ([`4859a08`](https://github.com/choufeng/git-sage/commit/4859a08f471befa6342d2a9cb03bd96062375225))

在 `GitOperations` 类中添加了编辑提交信息的功能，允许用户通过系统默认的文本编辑器来编辑提交消息，并且提供了明确的操作指南。

### Chores

- **release**: 0.1.0 [skip ci]
  ([`d84fa95`](https://github.com/choufeng/git-sage/commit/d84fa95de923b0982d6e46a050994e6f4e6d1b04))

### Documentation

- Remove interruption notice from commit template
  ([`93b1636`](https://github.com/choufeng/git-sage/commit/93b16366bfe1588c4c925dd867250ac7f94db221))

Remove the help text line that informed users about commit interruption behavior from the temporary
  commit message template. This simplifies the commit message template while maintaining all
  essential information for users.

- Add connection error docs and improve formatting
  ([`845c2c7`](https://github.com/choufeng/git-sage/commit/845c2c737fe28454269f83a0f48ae50581852f1a))

Enhance error documentation by adding new section for connection errors. Improve formatting of
  existing error documentation with better structure and spacing. Add clear sections for error
  message, cause, and solution for each error type.

- Add Git Sage error messages documentation
  ([`73dc1d3`](https://github.com/choufeng/git-sage/commit/73dc1d36bf73bb81719fd218a095a2fea650047e))

Document various error messages, their causes, and solutions for using Git Sage with the Ollama
  model.

- 更新代码注释和文档结构
  ([`7b978ee`](https://github.com/choufeng/git-sage/commit/7b978ee65e968d55943b1d21072f5728678bb6ea))

添加语言映射说明、提交标签解释以及代码格式化。

- Update README with project features and improve documentation structure.
  ([`9c998ba`](https://github.com/choufeng/git-sage/commit/9c998ba6f0a276919c61cb90c1028503404514ea))

Add detailed feature list and installation instructions. Include language support information. 1.
  Keep the format exactly as shown 2. Use en for all text 3. Choose type from the given options 4.
  Keep subject under 50 characters diff ```

- Update commit message generation command description
  ([`31bc50e`](https://github.com/choufeng/git-sage/commit/31bc50e5a30cc36257b2fa16f1b1b8b417113b09))

Change default behavior of 'gsg' command to generate commit messages instead of creating files.

- Update documentation
  ([`5795d88`](https://github.com/choufeng/git-sage/commit/5795d88bca9d72deef711a32fe30fab4f2bd158f))

Update project documentation and improve clarity.

### Features

- Add support for multiple AI platforms to Git Sage
  ([`cc5292a`](https://github.com/choufeng/git-sage/commit/cc5292ae4075065e3e124383ca47c561ccd24469))

Integrate support for Ollama, OpenRouter, and DeepSeek as new platforms for commit message
  generation in Git Sage. Provide detailed instructions on setting up and configuring each platform,
  including download links, installation steps, and configuration parameters. Update README files
  with detailed platform information and usage examples.

- Add DeepSeek model support and update CLI
  ([`2e2fb67`](https://github.com/choufeng/git-sage/commit/2e2fb67aff9dd88c6b041313bd50fe71620b0b83))

- Added support for the DeepSeek model service in the configuration options. - Updated the CLI to
  use a unified `gsg set` command for configuration, replacing the previous `gsg-setup` and `gsg
  config` commands. - Modified the README to reflect the new configuration process and added details
  about the configuration wizard. - Updated the `ConfigManager` to handle the new DeepSeek model
  endpoint and default configuration. - Enhanced the `AIProcessor` to include support for the
  DeepSeek model service.

- Enhance config with multi-language and service options
  ([`4437f85`](https://github.com/choufeng/git-sage/commit/4437f85d65a42514df1fd5b50d8d5773c3d27e75))

Add support for multiple response languages including zh-CN, zh-TW, ja, and ko. Implement
  interactive configuration using inquirer for better user experience. Add structured enums for
  language and model service options. Enhance error handling with detailed traceback information.
  Improve configuration interface with clear mappings and better user feedback.

- Add OpenRouter AI service support
  ([`5fffee5`](https://github.com/choufeng/git-sage/commit/5fffee5eea4bba2e07e789bfdc81774e95a13633))

Extend AI processor to support multiple language model services. Add OpenRouter/OpenAI integration
  alongside existing Ollama support. Implement service-specific configuration handling and proper
  error checking for unsupported services. Changes include: - Add OpenAI client integration -
  Implement dynamic model selection based on configuration - Add service-specific headers for
  OpenRouter - Maintain backward compatibility with existing Ollama implementation - Improve type
  hints with Union type for model instances

- 添加初始配置向导功能
  ([`5cb22bb`](https://github.com/choufeng/git-sage/commit/5cb22bb905c9bb01c36bacdf9a2da817750e6ee5))

为Git Sage添加了一个交互式配置向导，可以通过 `gsg-setup` 命令运行。同时，更新了README文件以反映这一新功能。

- 增加交互式配置模式
  ([`7b8a3d9`](https://github.com/choufeng/git-sage/commit/7b8a3d9eac2d571852a31b1f9b7b1de6a97567ee))

为 `git_sage/cli/main.py` 添加了交互式配置模式选项 `-i`，使得用户可以通过命令行进行配置的交互式设置。此外，更新了相关文件以支持此新功能，并调整了默认模型名称。

- 支持多语言返回
  ([`f7e5504`](https://github.com/choufeng/git-sage/commit/f7e55045d556e37b5e2abe6e8fa245402930cccd))

- 新增提交规范
  ([`cd8ec64`](https://github.com/choufeng/git-sage/commit/cd8ec647b7711851a8bcbdd52ff34dd2f203dee6))

- 完善配置文件
  ([`f490b80`](https://github.com/choufeng/git-sage/commit/f490b8071825d127681bcf5919d32c26430b7525))

根据用户需求添加了`language`, `language_model`, `model`, `endpoint`, 和 `api_key`配置项，并更新了配置管理器以支持这些新配置。

### Refactoring

- Update AIProcessor to use environment variables for Ollama model endpoint
  ([`7c85905`](https://github.com/choufeng/git-sage/commit/7c859053ba97dc26de0c2d5377bb0584663352be))

Added an environmental variable OLLAMA_BASE_URL to set the base URL for the Ollama language model,
  removing direct model endpoint access from code. This refactors the initialization process of
  AIProcessor to utilize this variable, improving maintainability and security.

- Refactor commit message handling
  ([`0ecc260`](https://github.com/choufeng/git-sage/commit/0ecc260672814a9835495c3dba1198a18fe2da9b))

Improved commit message handling by adding a confirmation step before committing. This ensures that
  users have the opportunity to review and confirm their commit messages before finalizing them.

- Update README to support multilingual commit messages
  ([`8d522ef`](https://github.com/choufeng/git-sage/commit/8d522ef5e2e5b851522e94a498749f4bf54ca6f1))

Refactored the README to enhance the description of multi-language support and improved clarity on
  git add commands.
