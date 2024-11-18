import click
import subprocess
import sys

def run_config():
    """运行配置命令"""
    try:
        # 使用gsg而不是git_sage.cli.main
        subprocess.run(["gsg", "config", "-i"], check=True)
    except subprocess.CalledProcessError:
        click.echo("配置过程中出现错误。你可以稍后使用 'gsg config -i' 命令重新配置。")
    except Exception as e:
        click.echo(f"发生错误: {str(e)}")
        click.echo("你可以稍后使用 'gsg config -i' 命令进行配置。")

@click.command()
def main():
    """初始化配置命令"""
    click.echo("\n=== Git Sage 初始配置 ===")
    if click.confirm("是否现在进行配置？", default=True):
        run_config()
    else:
        click.echo("\n你可以随时使用 'gsg config -i' 命令进行配置。")

if __name__ == '__main__':
    main()
