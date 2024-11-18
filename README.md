# Git Sage

[中文文档](README_CN.md)

Git Sage is an AI-powered Git assistant that helps you generate better commit messages.

## Features

- Automatically analyze staged changes
- Generate standardized commit messages using AI
- Support for both English and Chinese commit messages
- Customizable AI model configuration
- Simple and easy-to-use command line interface

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/git-sage.git

# Navigate to project directory
cd git-sage

# Install
pip install -e .

# Configure Git Sage
gsg set
```

## Configuration

Configure Git Sage settings:
```bash
# Set up configuration through interactive mode
gsg set

# View current configuration
gsg show config
```

The configuration wizard will guide you through setting up:
- Response language
- Language model service
- Model name
- Service endpoint
- API key

## Usage

Generate commit message:

```bash
# First stage your changes using git add
git add .

# Then use gsg to generate commit message and commit
gsg c
```

## Commit Message Convention

Commit messages follow the Conventional Commit specification with the following format:

```
{tag}: subject or title of the change
Optional detailed description
```

### Commit Tags Explanation

#### Patch Version (PATCH)
The following tags will trigger a patch version update:

- `Fix`: For bug fixes
- `Build`: For build process changes only
- `Maint`/`Maintenance`: For small maintenance tasks like technical debt cleanup, refactoring, build process changes, and non-breaking dependency updates
- `Test`: For application end-to-end tests
- `Patch`: Generic patch tag when other patch tags don't apply

#### Minor Version (MINOR)
The following tags will trigger a minor version update:

- `Feat`/`Feature`/`New`: For implementing new features
- `Minor`: Generic minor tag when other minor tags don't apply
- `Update`: For backward-compatible enhancements to existing features

#### Major Version (MAJOR)
The following tags will trigger a major version update:

- `Breaking`: For backward-incompatible enhancements or features
- `Major`: Generic major tag when other major tags don't apply

#### No Version Update (NO-OP)
The following tags will not trigger a version update:

- `Docs`: For documentation changes only
- `Chore`: For other changes that don't affect the actual environment, such as code comments, changes to non-package/application files, unit tests, etc.

## Configuration Details

The configuration file is located at `~/.git-sage/config.yml` and contains the following settings:

- language: Commit message language (defaults to en)
- language_model: Choose the language model service to use (defaults to ollama)
- model: Choose the specific model name (defaults to codellama)
- endpoint: Model service address (defaults to http://localhost:11434)
- api_key: API key (defaults to ollama)

You can view current configuration using `gsg show config` and modify settings through `gsg set`.

## Dependencies

- Python >= 3.8
- langgraph >= 0.2.50
- gitpython >= 3.1.40
- click >= 8.1.7
- pyyaml >= 6.0.1

## License

MIT License
