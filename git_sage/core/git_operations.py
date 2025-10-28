import os
import tempfile
import subprocess
import re
from typing import List, Tuple, Optional, Dict
from git import Repo, GitCommandError

class GitOperations:
    def __init__(self):
        self.repo = self._get_repo()
    
    def _get_repo(self) -> Repo:
        """Get Git repository for current directory"""
        try:
            return Repo(os.getcwd(), search_parent_directories=True)
        except Exception as e:
            raise Exception("Not a git repository") from e
    
    def get_staged_files(self) -> List[str]:
        """Get list of files that have been git added"""
        try:
            staged_files = []
            
            # Get modified files in staging area
            if self.repo.head.is_valid():
                diff_staged = self.repo.git.diff("--cached", "--name-only").split('\n')
                staged_files.extend([f for f in diff_staged if f])
            else:
                # For initial commit, get all staged files
                staged_files.extend([item.a_path for item in self.repo.index.diff(None)])
                # Get all new files added to staging area
                for entry in self.repo.index.entries:
                    if isinstance(entry, tuple) and len(entry) > 0:
                        staged_files.append(entry[0])
                    elif isinstance(entry, str):
                        staged_files.append(entry)
                
            return list(set(staged_files))  # Remove duplicates
        except Exception as e:
            raise Exception(f"Failed to get staged files: {e}") from e
    
    def get_staged_diff(self) -> str:
        """Get changes in staged files"""
        try:
            # Get differences between staging area and HEAD
            if self.repo.head.is_valid():
                diff = self.repo.git.diff("--cached")
            else:
                # For initial repository, show content of files in staging area
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
        Commit changes
        :param message: Commit message
        :param confirm: Whether to require edit confirmation
        :return: Whether commit was successful
        """
        try:
            if confirm:
                # Create temporary file for editing commit message
                with tempfile.NamedTemporaryFile(mode='w+', suffix='.tmp', delete=False) as temp_file:
                    temp_file.write(message)
                    temp_file.write("\n\n# Please edit your commit message above.")
                    temp_file.write("\n# Save and exit the editor to proceed with the commit.")
                    temp_file_path = temp_file.name

                try:
                    # Open temporary file with system default editor
                    editor = os.environ.get('EDITOR', 'vim')
                    os.system(f'{editor} {temp_file_path}')

                    # Read edited commit message
                    with open(temp_file_path, 'r') as temp_file:
                        edited_message = ''
                        for line in temp_file:
                            if not line.startswith('#'):
                                edited_message += line
                        edited_message = edited_message.strip()

                    # Cancel commit only if message is empty
                    if not edited_message:
                        print("Commit message is empty, commit cancelled.")
                        return False
                    
                    # Ask user to confirm commit
                    confirm_input = input("\nConfirm commit? [Y/n] ").strip().lower()
                    if confirm_input == '' or confirm_input == 'y':
                        # Execute commit
                        self.repo.index.commit(edited_message)
                        print("Commit completed.")
                        return True
                    else:
                        print("Commit cancelled.")
                        return False

                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(temp_file_path)
                    except:
                        pass
            else:
                # If no confirmation needed, commit directly
                self.repo.index.commit(message)
                return True

        except Exception as e:
            raise Exception(f"Failed to commit: {e}") from e
    
    def has_staged_changes(self) -> bool:
        """Check if there are staged changes"""
        try:
            # Use get_staged_files to check for staged files
            staged_files = self.get_staged_files()
            return len(staged_files) > 0
        except Exception as e:
            raise Exception(f"Failed to check staged changes: {e}") from e

    def is_git_repository(self) -> bool:
        """Check if current directory is a git repository"""
        try:
            self.repo.git.rev_parse('--is-inside-work-tree')
            return True
        except GitCommandError:
            return False
            
    def _branch_exists(self, branch_name: str) -> bool:
        """Check if branch exists locally or remotely"""
        try:
            # Check if remote branch exists
            remote_branches = [ref.name for ref in self.repo.remote('origin').refs]
            if f'origin/{branch_name}' in remote_branches:
                return True
            
            # Check if local branch exists
            local_branches = [ref.name for ref in self.repo.heads]
            if branch_name in local_branches:
                return True
                
            return False
        except Exception:
            # If we can't check, assume it might exist
            return True
    
    def get_main_branch_name(self) -> str:
        """Get the name of the main branch using multiple detection strategies"""
        print("检测主分支名称...")
        
        # Strategy 1: Check remote HEAD
        try:
            remote_head = self.repo.git.symbolic_ref('refs/remotes/origin/HEAD')
            branch_name = remote_head.split('/')[-1]
            if self._branch_exists(branch_name):
                print(f"从远程 HEAD 检测到主分支: {branch_name}")
                return branch_name
            else:
                print(f"远程 HEAD 指向的分支 '{branch_name}' 不存在")
        except GitCommandError:
            print("无法从远程 HEAD 获取主分支信息")
        
        # Strategy 2: Check common main branch names
        common_branches = ['main', 'master', 'develop']
        print(f"检查常见主分支名称: {common_branches}")
        
        for branch in common_branches:
            if self._branch_exists(branch):
                print(f"找到存在的主分支: {branch}")
                return branch
        
        # Strategy 3: Fallback - use 'main' as default
        print("使用默认主分支名称: main")
        return 'main'
            
    def get_branch_diff(self) -> Optional[str]:
        """Get diff between current branch and main branch"""
        try:
            main_branch = self.get_main_branch_name()
            return self.repo.git.diff(f'{main_branch}...HEAD')
        except GitCommandError as e:
            print(f"Warning: Failed to get branch diff: {e}")
            return None
    
    def get_current_branch(self) -> str:
        """Get current branch name"""
        try:
            return self.repo.active_branch.name
        except Exception as e:
            raise Exception(f"Failed to get current branch: {e}") from e
    
    def get_branch_commits(self) -> List[Dict[str, str]]:
        """Get commits in current branch that are not in main branch"""
        try:
            main_branch = self.get_main_branch_name()
            current_branch = self.get_current_branch()
            
            # Get commits that are in current branch but not in main branch
            commits = list(self.repo.iter_commits(f'{main_branch}..{current_branch}'))
            
            commit_list = []
            for commit in commits:
                commit_list.append({
                    'hash': commit.hexsha[:7],
                    'message': commit.message.strip(),
                    'author': str(commit.author),
                    'date': commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return commit_list
        except Exception as e:
            raise Exception(f"Failed to get branch commits: {e}") from e
    
    def extract_ticket_from_branch(self) -> Optional[str]:
        """Extract ticket number from branch name"""
        try:
            branch_name = self.get_current_branch()
            
            # Pattern to match ticket numbers like IM-2312, JIRA-123, etc.
            pattern = r'([A-Z]+-\d+)'
            match = re.search(pattern, branch_name)
            
            if match:
                return match.group(1)
            return None
        except Exception as e:
            print(f"Warning: Failed to extract ticket from branch: {e}")
            return None
    
    def has_github_cli(self) -> bool:
        """Check if GitHub CLI (gh) is installed"""
        try:
            subprocess.run(['gh', '--version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def push_branch(self) -> bool:
        """Push current branch to remote"""
        try:
            current_branch = self.get_current_branch()
            origin = self.repo.remote('origin')
            
            # Push current branch to origin
            origin.push(current_branch)
            return True
        except Exception as e:
            print(f"Failed to push branch: {e}")
            return False
    
    def get_remote_url(self) -> Optional[str]:
        """Get remote origin URL"""
        try:
            return self.repo.remote('origin').url
        except Exception as e:
            print(f"Warning: Failed to get remote URL: {e}")
            return None
    
    def edit_pr_content(self, pr_content: Dict[str, str], allow_edit: bool = True) -> Optional[Dict[str, str]]:
        """
        Allow user to edit PR content (title and description)
        :param pr_content: Dictionary with 'title' and 'description' keys
        :param allow_edit: Whether to allow editing
        :return: Edited PR content or None if cancelled
        """
        try:
            if not allow_edit:
                return pr_content
            
            # Create temporary file for editing PR content
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False) as temp_file:
                # Write PR content in a structured format
                temp_file.write(f"# PR Title\n{pr_content['title']}\n\n")
                temp_file.write(f"# PR Description\n{pr_content['description']}\n\n")
                temp_file.write("\n# 请编辑上面的 PR 标题和描述内容")
                temp_file.write("\n# 保存并退出编辑器以继续创建 PR")
                temp_file.write("\n# 标题行应该在 '# PR Title' 下面")
                temp_file.write("\n# 描述内容应该在 '# PR Description' 下面")
                temp_file_path = temp_file.name

            try:
                # Open temporary file with system default editor
                editor = os.environ.get('EDITOR', 'vim')
                os.system(f'{editor} {temp_file_path}')

                # Read edited content
                with open(temp_file_path, 'r', encoding='utf-8') as temp_file:
                    content = temp_file.read()
                
                # Parse the edited content
                edited_content = self._parse_pr_content(content)
                
                if not edited_content['title'].strip():
                    print("PR 标题为空，操作已取消。")
                    return None
                
                return edited_content

            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            raise Exception(f"Failed to edit PR content: {e}") from e
    
    def _parse_pr_content(self, content: str) -> Dict[str, str]:
        """
        Parse edited PR content from temporary file
        :param content: Raw content from temporary file
        :return: Dictionary with parsed title and description
        """
        lines = content.split('\n')
        result = {'title': '', 'description': ''}
        
        current_section = None
        title_lines = []
        description_lines = []
        
        for line in lines:
            # Skip comment lines
            if line.strip().startswith('#'):
                if 'PR Title' in line:
                    current_section = 'title'
                elif 'PR Description' in line:
                    current_section = 'description'
                continue
            
            # Add content to appropriate section
            if current_section == 'title' and line.strip():
                title_lines.append(line.strip())
                current_section = None  # Only take the first non-empty line after title header
            elif current_section == 'description':
                description_lines.append(line)
        
        # Join the collected lines
        result['title'] = ' '.join(title_lines) if title_lines else ''
        result['description'] = '\n'.join(description_lines).strip()
        
        return result
