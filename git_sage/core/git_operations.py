import os
import tempfile
from typing import List, Tuple, Optional
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
            
    def get_main_branch_name(self) -> str:
        """Get the name of the main branch"""
        try:
            remote_head = self.repo.git.symbolic_ref('refs/remotes/origin/HEAD')
            return remote_head.split('/')[-1]
        except GitCommandError:
            return 'main'
            
    def get_branch_diff(self) -> Optional[str]:
        """Get diff between current branch and main branch"""
        try:
            main_branch = self.get_main_branch_name()
            return self.repo.git.diff(f'{main_branch}...HEAD')
        except GitCommandError as e:
            print(f"Warning: Failed to get branch diff: {e}")
            return None
