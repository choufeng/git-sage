import click
import inquirer
from enum import Enum
from git_sage.config.config_manager import ConfigManager
from git_sage.core.git_operations import GitOperations
from git_sage.core.ai_processor import AIProcessor

class ResponseLanguage(str, Enum):
    ENGLISH = 'en'
    SIMPLIFIED_CHINESE = 'zh-CN'
    TRADITIONAL_CHINESE = 'zh-TW'
    JAPANESE = 'ja'
    KOREAN = 'ko'

class ModelService(str, Enum):
    OLLAMA = 'ollama'
    OPENROUTER = 'openrouter'

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
@click.option('--interactive', '-i', is_flag=True, help='Interactive configuration mode')
@click.option('--language', type=click.Choice(['en', 'zh-CN', 'zh-TW', 'ja', 'ko']), help='Set response language')
@click.option('--language-model', type=str, help='Set language model service (e.g., ollama)')
@click.option('--model', type=str, help='Set specific model name (e.g., codellama)')
@click.option('--endpoint', type=str, help='Set model service endpoint')
@click.option('--api-key', type=str, help='Set API key')
def config(interactive, language, language_model, model, endpoint, api_key):
    """Configure Git Sage settings"""
    try:
        config_manager = ConfigManager()
        current_config = config_manager.config

        if interactive:
            click.echo("\n=== Interactive Configuration Mode ===\n")
            
            # Language mapping
            lang_map = {
                'English': 'en',
                '简体中文': 'zh-CN',
                '繁體中文': 'zh-TW',
                '日本語': 'ja',
                '한국어': 'ko'
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
                'OpenRouter': 'openrouter'
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
            
        else:
            if language:
                config_manager.update_config('language', language)
                click.echo(f"Response language set to: {language}")
                
            if language_model:
                config_manager.update_config('language_model', language_model)
                click.echo(f"Language model service set to: {language_model}")
                
            if model:
                config_manager.update_config('model', model)
                click.echo(f"Model name set to: {model}")
                
            if endpoint:
                config_manager.update_config('endpoint', endpoint)
                click.echo(f"Model endpoint set to: {endpoint}")
                
            if api_key:
                config_manager.update_config('api_key', api_key)
                click.echo("API key updated")
            
            if not any([language, language_model, model, endpoint, api_key]):
                # Display current configuration
                click.echo("\nCurrent configuration:")
                click.echo(f"Response Language: {current_config['language']}")
                click.echo(f"Language Model Service: {current_config['language_model']}")
                click.echo(f"Model Name: {current_config['model']}")
                click.echo(f"Model Endpoint: {current_config['endpoint']}")
                click.echo(f"API key: {'*' * 8}")
            
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

if __name__ == '__main__':
    cli()
