import os
from typing import List, Tuple, Optional
from git import Repo, GitCommandError

class GitOperations:
    def __init__(self):
        self.repo = self._get_repo()
    
    def _get_repo(self) -> Repo:
        """获取当前目录的Git仓库"""
        try:
            return Repo(os.getcwd(), search_parent_directories=True)
        except Exception as e:
            raise Exception("Not a git repository") from e
    
    def get_staged_files(self) -> List[str]:
        """获取已经git add的文件列表"""
        try:
            staged_files = []
            
            # 获取已暂存的修改文件
            if self.repo.head.is_valid():
                diff_staged = self.repo.git.diff("--cached", "--name-only").split('\n')
                staged_files.extend([f for f in diff_staged if f])
            else:
                # 如果是初始提交，获取所有暂存的文件
                staged_files.extend([item.a_path for item in self.repo.index.diff(None)])
                # 获取所有已添加到暂存区的新文件
                for entry in self.repo.index.entries:
                    if isinstance(entry, tuple) and len(entry) > 0:
                        staged_files.append(entry[0])
                    elif isinstance(entry, str):
                        staged_files.append(entry)
                
            return list(set(staged_files))  # 去重
        except Exception as e:
            raise Exception(f"Failed to get staged files: {e}") from e
    
    def get_staged_diff(self) -> str:
        """获取已暂存文件的更改内容"""
        try:
            # 获取暂存区和HEAD之间的差异
            if self.repo.head.is_valid():
                diff = self.repo.git.diff("--cached")
            else:
                # 如果是初始仓库，显示暂存区中的文件内容
                diff = ""
                for file_path in self.get_staged_files():
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                        diff += f"diff --git a/{file_path} b/{file_path}\n"
                        diff += f"new file mode 100644\n"
                        diff += f"--- /dev/null\n"
                        diff += f"+++ b/{file_path}\n"
                        diff += "".join(f"+{line}" for line in content.splitlines(True))
                        diff += "\n"
                    except Exception as e:
                        print(f"Warning: Could not read file {file_path}: {e}")
            return diff
        except Exception as e:
            raise Exception(f"Failed to get diff: {e}") from e
    
    def commit(self, message: str, confirm: bool = True) -> bool:
        """
        提交更改
        :param message: 提交信息
        :param confirm: 是否需要确认
        :return: 是否提交成功
        """
        try:
            if confirm:
                print("\nCommit message:")
                print("-" * 50)
                print(message)
                print("-" * 50)
                response = input("\nDo you want to proceed with this commit? [y/N]: ")
                if response.lower() != 'y':
                    print("Commit cancelled.")
                    return False
            
            self.repo.index.commit(message)
            return True
        except Exception as e:
            raise Exception(f"Failed to commit: {e}") from e
    
    def has_staged_changes(self) -> bool:
        """检查是否有已暂存的更改"""
        try:
            # 使用 get_staged_files 来检查是否有暂存的文件
            staged_files = self.get_staged_files()
            return len(staged_files) > 0
        except Exception as e:
            raise Exception(f"Failed to check staged changes: {e}") from e
