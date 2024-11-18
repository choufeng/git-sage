import os
import tempfile
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
        :param confirm: 是否需要编辑确认
        :return: 是否提交成功
        """
        try:
            if confirm:
                # 创建临时文件来编辑提交信息
                with tempfile.NamedTemporaryFile(mode='w+', suffix='.tmp', delete=False) as temp_file:
                    temp_file.write(message)
                    temp_file.write("\n\n# 请在上方编辑您的提交信息。")
                    temp_file.write("\n# 保存并退出编辑器将执行提交操作。")
                    temp_file.write("\n# 中断编辑将取消提交。")
                    temp_file_path = temp_file.name

                try:
                    # 使用系统默认编辑器打开临时文件
                    editor = os.environ.get('EDITOR', 'vim')
                    exit_code = os.system(f'{editor} {temp_file_path}')
                    
                    if exit_code != 0:
                        print("提交已取消。")
                        return False

                    # 读取编辑后的提交信息
                    with open(temp_file_path, 'r') as temp_file:
                        edited_message = ''
                        for line in temp_file:
                            if not line.startswith('#'):
                                edited_message += line
                        edited_message = edited_message.strip()

                    if not edited_message:
                        print("提交信息为空，提交已取消。")
                        return False

                    # 执行提交
                    self.repo.index.commit(edited_message)
                    return True

                finally:
                    # 清理临时文件
                    try:
                        os.unlink(temp_file_path)
                    except:
                        pass
            else:
                # 如果不需要确认，直接提交
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
