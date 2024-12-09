import os
import json
from typing import Dict, List, Optional, Union
from ..config.config_manager import ConfigManager
from .ai_processor import AIProcessor
from .git_operations import GitOperations

class CodeValidator:
    def __init__(self, ai_processor: AIProcessor, git_ops: GitOperations):
        """Initialize the code validator with necessary dependencies."""
        self.ai_processor = ai_processor
        self.git_ops = git_ops
        self.config_prompts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'prompts')
        self.user_prompts_dir = os.path.expanduser('~/.git-sage/prompts')

    def _load_prompt(self, prompt_name: str) -> Optional[str]:
        """Load prompt from user directory first, then fall back to config directory"""
        # Try user directory first
        user_prompt_path = os.path.join(self.user_prompts_dir, f'{prompt_name}.txt')
        if os.path.exists(user_prompt_path):
            try:
                with open(user_prompt_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            except Exception:
                pass
                
        # Fall back to config directory
        config_prompt_path = os.path.join(self.config_prompts_dir, f'{prompt_name}.txt')
        if os.path.exists(config_prompt_path):
            try:
                with open(config_prompt_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            except Exception:
                pass
                
        return None
        
    def validate_changes(self, prompt_type: str) -> Dict:
        """Validate changes using specified prompt type"""
        # Load prompts
        common_prompt = self._load_prompt('common')
        specific_prompt = self._load_prompt(prompt_type)
        
        if not common_prompt or not specific_prompt:
            return {
                "status": "ERROR",
                "message": f"无法加载 prompt 文件。请确保以下文件存在：\n"
                          f"1. {self.user_prompts_dir}/common.txt 或 {self.config_prompts_dir}/common.txt\n"
                          f"2. {self.user_prompts_dir}/{prompt_type}.txt 或 {self.config_prompts_dir}/{prompt_type}.txt"
            }
            
        # Get diff
        diff = self.git_ops.get_branch_diff()
        if not diff:
            return {
                "status": "ERROR",
                "message": "没有发现代码变更，请确保：\n1. 当前分支有提交的改动\n2. 当前分支与主分支有差异"
            }
            
        # Combine prompts
        full_prompt = f"{common_prompt}\n{specific_prompt}\n\n以下是代码变更：\n{diff}"
        
        # Get AI feedback
        try:
            response = self.ai_processor.get_response(full_prompt)
            return {
                "status": "PASS" if "符合规范" in response or "质量良好" in response else "FAIL",
                "message": response
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"获取 AI 反馈失败：{str(e)}"
            }
            
    def format_validation_result(self, result: Dict) -> str:
        """Format validation result for display"""
        status_map = {
            "PASS": "✅ 通过",
            "FAIL": "❌ 未通过",
            "ERROR": "⚠️ 错误"
        }
        
        return f"{status_map.get(result['status'], '❓ 未知')}\n\n{result['message']}"
