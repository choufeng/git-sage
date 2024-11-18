import click
import subprocess
import sys
import traceback

def main():
    """Initialize configuration command"""
    print("\n=== Git Sage Initial Setup ===")
    if click.confirm("Would you like to configure Git Sage now?", default=True):
        try:
            subprocess.run(["gsg", "config", "-i"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"\nAn error occurred during configuration: {str(e)}")
            print("You can reconfigure using 'gsg config -i' later.")
        except Exception as e:
            print(f"\nError occurred: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            print("\nYou can configure Git Sage anytime using 'gsg config -i'.")
    else:
        print("\nYou can configure Git Sage anytime using 'gsg config -i'.")

if __name__ == '__main__':
    main()
