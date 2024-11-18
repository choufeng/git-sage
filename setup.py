from setuptools import setup, find_packages

setup(
    name="git-sage",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'langgraph>=0.2.50',
        'gitpython>=3.1.40',
        'click>=8.1.7',
        'pyyaml>=6.0.1',
        'requests>=2.31.0',
        'langchain-community>=0.0.10',
        'langchain-ollama>=0.2.0',
        'langchain-core>=0.3.0',
        'langchain-openai>=0.0.5',
        'openai>=1.0.0',
        'ollama>=0.3.0',
        'inquirer>=3.1.3',
    ],
    entry_points={
        'console_scripts': [
            'gsg=git_sage.cli.main:cli',
        ],
    },
    python_requires='>=3.8',
    author="Git Sage Team",
    author_email="",
    description="An AI-powered Git assistant that helps with commit messages",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/git-sage",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
