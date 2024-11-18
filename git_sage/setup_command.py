import click
import subprocess
import sys

def main():
    """初始化配置命令"""
    print("\n=== Git Sage 初始配置 ===")
    if click.confirm("是否现在进行配置？", default=True):
        try:
            subprocess.run(["gsg", "config", "-i"], check=True)
        except subprocess.CalledProcessError:
            print("\n配置过程中出现错误。你可以稍后使用 'gsg config -i' 命令重新配置。")
        except Exception as e:
            print(f"\n发生错误: {str(e)}")
            print("你可以稍后使用 'gsg config -i' 命令进行配置。")
    else:
        print("\n你可以随时使用 'gsg config -i' 命令进行配置。")

if __name__ == '__main__':
    main()
