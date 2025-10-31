import click
import inquirer
import subprocess
from enum import Enum
from typing import Dict
from git_sage.config.config_manager import ConfigManager
from git_sage.core.git_operations import GitOperations
from git_sage.core.ai_processor import AIProcessor
from git_sage.core.code_validator import CodeValidator
import os
import sys

class ResponseLanguage(str, Enum):
    ENGLISH = 'en'
    SIMPLIFIED_CHINESE = 'zh-CN'
    TRADITIONAL_CHINESE = 'zh-TW'

class ModelService(str, Enum):
    OLLAMA = 'ollama'
    OPENROUTER = 'openrouter'
    DEEPSEEK = 'deepseek'
    GEMINI = 'gemini'
    MODELSCOPE = 'modelscope'

@click.group()
def cli():
    """Git Sage - Your AI-powered Git assistant"""
    pass

@cli.command()
@click.argument('files', nargs=-1)
def c(files):
    """Analyze staged changes and generate commit message"""
    try:
        # Initialize modules
        config_manager = ConfigManager()
        git_ops = GitOperations()
        ai_processor = AIProcessor(config_manager)
        
        # Check for staged changes
        if not git_ops.has_staged_changes():
            click.echo("No staged changes found. Please 'git add' some files first.")
            return
        
        # Get diff content
        diff_content = git_ops.get_staged_diff()
        if not diff_content:
            click.echo("No changes to analyze.")
            return
        
        # Process diff content with AI
        click.echo("Analyzing changes...")
        commit_message = ai_processor.process_diff(diff_content)
        
        # Execute commit
        if git_ops.commit(commit_message):
            click.echo("Changes committed successfully!")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

@cli.command()
@click.argument('rule_type', required=False, default='common')
@click.argument('files', nargs=-1)
def v(rule_type, files):
    """Verify staged changes against predefined rules. 
    Optionally specify a rule type (e.g., 'c' for conventional commit rules)"""
    try:
        # Initialize modules
        config_manager = ConfigManager()
        git_ops = GitOperations()
        ai_processor = AIProcessor(config_manager)
        code_validator = CodeValidator(ai_processor, git_ops)
        
        # Check for staged changes
        if not git_ops.has_staged_changes():
            click.echo("No staged changes found. Please 'git add' some files first.")
            return
            
        # Verify the prompt file exists
        prompt_file = f"{rule_type}.txt"
        prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                'config', 'prompts', prompt_file)
        
        if not os.path.exists(prompt_path):
            click.echo(f"Rule type '{rule_type}' not found. Please check available rules in the prompts directory.")
            return
            
        # Run validation
        click.echo(f"Verifying changes using rule type: {rule_type}")
        result = code_validator.validate_changes(rule_type)
        
        # Display results
        click.echo("\nValidation Results:")
        click.echo(code_validator.format_validation_result(result))
        
        # Exit with appropriate status code
        if result["status"] != "PASS":
            sys.exit(1)
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('prompt', required=False, default='ccr')
def cr(prompt):
    """检查当前分支与主分支的代码差异"""
    try:
        # Initialize modules
        config_manager = ConfigManager()
        git_ops = GitOperations()
        ai_processor = AIProcessor(config_manager)
        code_validator = CodeValidator(ai_processor, git_ops)
        
        # Check if in git repository
        if not git_ops.is_git_repository():
            click.echo("Error: 当前目录不是 git 仓库")
            sys.exit(1)
            
        # Get diff with main branch
        diff = git_ops.get_branch_diff()
        if not diff:
            click.echo("没有发现代码变更，请确保：\n1. 当前分支有提交的改动\n2. 当前分支与主分支有差异")
            return
            
        # Verify the prompt file exists
        prompt_file = f"{prompt}.txt"
        prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                'config', 'prompts', prompt_file)
        
        if not os.path.exists(prompt_path):
            click.echo(f"Error: 规则类型 '{prompt}' 不存在。请检查 prompts 目录中的可用规则。")
            sys.exit(1)
            
        # Run validation
        click.echo(f"正在使用规则 {prompt} 分析代码变更...")
        result = code_validator.validate_changes(prompt)
        
        # Display results
        click.echo("\n分析结果：")
        click.echo(code_validator.format_validation_result(result))
        
        # Exit with appropriate status code
        if result["status"] != "PASS":
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
def set():
    """Configure Git Sage settings through interactive mode"""
    try:
        config_manager = ConfigManager()
        current_config = config_manager.config

        click.echo("\n=== Git Sage Configuration ===\n")
        
        # Language mapping
        lang_map = {
            'English': 'en',
            '简体中文': 'zh-CN',
            '繁體中文': 'zh-TW'
        }
        
        # Reverse mapping for default value
        rev_lang_map = {v: k for k, v in lang_map.items()}
        
        # Response language configuration
        questions = [
            inquirer.List(
                'language',
                message="Response Language",
                choices=list(lang_map.keys()),
                default=rev_lang_map.get(current_config['language'], 'English')
            )
        ]
        
        answers = inquirer.prompt(questions)
        if not answers:
            return
        
        config_manager.update_config('language', lang_map[answers['language']])
        
        # Service mapping
        service_map = {
            'Ollama': 'ollama',
            'OpenRouter': 'openrouter',
            'DeepSeek': 'deepseek',
            'Gemini': 'gemini',
            'ModelScope': 'modelscope'
        }
        rev_service_map = {v: k for k, v in service_map.items()}
        
        # Language model service configuration
        questions = [
            inquirer.List(
                'language_model',
                message="Language Model Service",
                choices=list(service_map.keys()),
                default=rev_service_map.get(current_config['language_model'], 'Ollama')
            )
        ]
        
        answers = inquirer.prompt(questions)
        if not answers:
            return
            
        config_manager.update_config('language_model', service_map[answers['language_model']])
        
        # Model name configuration
        model = click.prompt(
            "Model Name",
            type=str,
            default=current_config['model']
        )
        config_manager.update_config('model', model)
        
        # Model endpoint configuration
        endpoint = click.prompt(
            "Model Endpoint",
            type=str,
            default=current_config['endpoint']
        )
        config_manager.update_config('endpoint', endpoint)
        
        # API key configuration
        api_key = click.prompt(
            "API Key",
            type=str,
            default=current_config['api_key']
        )
        config_manager.update_config('api_key', api_key)
        
        click.echo("\nConfiguration updated successfully!")
            
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

@cli.group()
def show():
    """Show Git Sage information"""
    pass

@show.command()
def config():
    """Show current configuration"""
    try:
        config_manager = ConfigManager()
        current_config = config_manager.config
        
        click.echo("\n=== Current Configuration ===\n")
        click.echo(f"Response Language: {current_config['language']}")
        click.echo(f"Language Model Service: {current_config['language_model']}")
        click.echo(f"Model Name: {current_config['model']}")
        click.echo(f"Model Endpoint: {current_config['endpoint']}")
        click.echo(f"API Key: {'*' * 8}")
        click.echo(f"\nConfig File: {config_manager.config_path}")
            
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

@cli.command()
def init_prompts():
    """Initialize default prompt files in user's directory"""
    try:
        # Create prompts directory
        prompts_dir = os.path.expanduser('~/.git-sage/prompts')
        os.makedirs(prompts_dir, exist_ok=True)
        
        # Define default prompts
        prompts = {
            'common.txt': '''你是一个专业的代码审查者。请仔细检查以下代码变更，并提供专业的建议。

请从以下几个方面进行评估：
1. 代码质量
2. 代码风格
3. 性能影响
4. 安全性
5. 可维护性

如果发现问题，请具体指出问题所在并给出改进建议。如果代码符合规范，请确认代码质量良好。''',
            
            'ccr.txt': '''你是一个专业的代码审查者。请仔细检查以下代码变更，并指出任何不符合以下规则的地方：

1. 代码风格是否统一且易读
2. 是否有潜在的性能问题
3. 是否有安全隐患
4. 是否有重复代码
5. 变量和函数命名是否清晰明确
6. 是否有适当的错误处理
7. 是否有充分的注释说明

请详细说明发现的问题，并给出改进建议。如果代码符合规范，请确认代码质量良好。'''
        }
        
        # Write prompt files
        for filename, content in prompts.items():
            file_path = os.path.join(prompts_dir, filename)
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                click.echo(f"Created {filename}")
            else:
                click.echo(f"Skipped {filename} (already exists)")
                
        click.echo(f"\nPrompt files initialized in {prompts_dir}")
        click.echo("You can now customize these files according to your needs.")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--dry-run', '-n', is_flag=True, help='仅显示PR信息，不创建')
@click.option('--no-verify', '-nv', is_flag=True, help='设置QA部分为None')
@click.option('--no-edit', is_flag=True, help='跳过编辑步骤，直接使用AI生成的内容')
def pr(dry_run, no_verify, no_edit):
    """生成并创建 Pull Request"""
    try:
        # Initialize modules
        config_manager = ConfigManager()
        git_ops = GitOperations()
        ai_processor = AIProcessor(config_manager)
        
        # Check if in git repository
        if not git_ops.is_git_repository():
            click.echo("错误：当前目录不是 git 仓库")
            sys.exit(1)
        
        # Get current branch
        current_branch = git_ops.get_current_branch()
        main_branch = git_ops.get_main_branch_name()
        
        # Check if on main branch
        if current_branch == main_branch:
            click.echo(f"错误：当前在主分支 '{main_branch}' 上，无法创建 PR")
            sys.exit(1)
        
        # Get branch commits and diff
        click.echo(f"正在分析分支 '{current_branch}' 的变更...")
        commits = git_ops.get_branch_commits()
        diff_content = git_ops.get_branch_diff()
        
        if not commits and not diff_content:
            click.echo("没有发现与主分支的差异，无法创建 PR")
            return
        
        # Extract ticket number from branch name
        ticket = git_ops.extract_ticket_from_branch()
        
        # Generate PR content using AI
        click.echo("正在生成 PR 内容...")
        pr_content = ai_processor.generate_pr_content(commits, diff_content, ticket, no_verify)
        
        # Allow user to edit PR content (unless --no-edit flag is used)
        if not no_edit and not dry_run:
            click.echo("\n允许编辑 PR 内容...")
            edited_content = git_ops.edit_pr_content(pr_content, allow_edit=True)
            if edited_content is None:
                click.echo("PR 创建已取消")
                return
            pr_content = edited_content
            click.echo("PR 内容编辑完成")
        
        # Display PR information
        click.echo("\n" + "="*50)
        click.echo("生成的 PR 信息：" if no_edit else "编辑后的 PR 信息：")
        click.echo("="*50)
        click.echo(f"标题: {pr_content['title']}")
        click.echo(f"\n描述:\n{pr_content['description']}")
        click.echo("="*50)
        
        if dry_run:
            click.echo("\n--dry-run 模式：仅显示信息，不创建 PR")
            return
        
        # Check if GitHub CLI is available
        if git_ops.has_github_cli():
            # Ask user if they want to create PR
            create_pr = click.confirm("\n是否创建 Pull Request?", default=True)
            
            if create_pr:
                # Check if branch is pushed to remote
                try:
                    click.echo("检查分支状态...")
                    # Try to get remote tracking branch
                    remote_branch = git_ops.repo.active_branch.tracking_branch()
                    if not remote_branch:
                        click.echo("分支尚未推送到远程，正在推送...")
                        if not git_ops.push_branch():
                            click.echo("推送分支失败")
                            sys.exit(1)
                        click.echo("分支推送成功")
                except:
                    # If tracking branch doesn't exist, push the branch
                    click.echo("分支尚未推送到远程，正在推送...")
                    if not git_ops.push_branch():
                        click.echo("推送分支失败")
                        sys.exit(1)
                    click.echo("分支推送成功")
                
                # Create PR using GitHub CLI
                try:
                    click.echo("正在创建 Pull Request...")
                    cmd = [
                        'gh', 'pr', 'create',
                        '--title', pr_content['title'],
                        '--body', pr_content['description']
                    ]
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    click.echo("Pull Request 创建成功！")
                    click.echo(f"PR URL: {result.stdout.strip()}")
                except subprocess.CalledProcessError as e:
                    click.echo(f"创建 PR 失败: {e.stderr}")
                    sys.exit(1)
            else:
                click.echo("PR 创建已取消")
        else:
            click.echo("\n未检测到 GitHub CLI (gh)，无法自动创建 PR")
            click.echo("请手动创建 PR，或安装 GitHub CLI: https://cli.github.com/")
            click.echo(f"\n当前分支: {current_branch}")
            click.echo(f"目标分支: {main_branch}")
            remote_url = git_ops.get_remote_url()
            if remote_url:
                click.echo(f"远程仓库: {remote_url}")
    
    except Exception as e:
        click.echo(f"错误: {str(e)}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()
