import os
import json
from typing import Dict, List, Optional, Union

class CodeValidator:
    def __init__(self, ai_processor, git_ops):
        """Initialize the code validator with necessary dependencies."""
        self.ai_processor = ai_processor
        self.git_ops = git_ops
        self.prompts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'prompts')

    def _load_prompt(self, prompt_file: str) -> str:
        """Load a prompt file from the prompts directory."""
        with open(os.path.join(self.prompts_dir, prompt_file), 'r') as f:
            return f.read()

    def _combine_prompts(self, rule_type: str) -> str:
        """Combine common rules with specific rule type."""
        common_prompt = self._load_prompt('common.txt')
        if rule_type == 'common':
            return common_prompt
            
        specific_prompt = self._load_prompt(f'{rule_type}.txt')
        return f"{common_prompt}\n\nAdditionally, apply these specific rules:\n\n{specific_prompt}"

    def validate_changes(self, rule_type: str) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        """
        Validate the staged changes against specified rules.
        
        Args:
            rule_type: Type of rules to apply (e.g., 'c' for conventional commit rules)
            
        Returns:
            Dict containing validation results with status, issues, and summary
        """
        try:
            # Get the diff of staged changes
            diff_content = self.git_ops.get_staged_diff()
            if not diff_content:
                return {
                    "status": "FAIL",
                    "issues": [],
                    "summary": "No changes to analyze"
                }

            # Load and combine prompts
            prompt = self._combine_prompts(rule_type)
            
            # Get AI analysis of the changes
            analysis = self.ai_processor.analyze_code(prompt, diff_content)
            
            # Debug: Print the raw AI response
            print("\nDebug - Raw AI response:")
            print(analysis)
            print("\n" + "="*50 + "\n")
            
            # Parse the AI response
            try:
                result = json.loads(analysis)
                # Ensure the response has the required fields
                required_fields = ['status', 'issues', 'summary']
                if not all(field in result for field in required_fields):
                    raise ValueError("AI response missing required fields")
                return result
            except json.JSONDecodeError as e:
                print(f"\nDebug - JSON parse error: {str(e)}")
                return {
                    "status": "ERROR",
                    "issues": [],
                    "summary": "Failed to parse AI response"
                }

        except Exception as e:
            return {
                "status": "ERROR",
                "issues": [],
                "summary": f"Error during validation: {str(e)}"
            }

    def format_validation_result(self, result: Dict[str, Union[str, List[Dict[str, str]]]]) -> str:
        """Format the validation result for display in Chinese."""
        output = []
        
        if result["status"] == "PASS":
            output.append("✅ 验证通过！所有检查都符合规范。")
        elif result["status"] == "ERROR":
            output.append(f"❌ 验证过程中出现错误：{result['summary']}")
        else:
            output.append("❌ 发现以下问题：")
            
        if result.get("issues"):
            for issue in result["issues"]:
                file_info = f"{issue['file']}:{issue.get('line', 'N/A')}"
                output.append(f"\n• 位置：{file_info}")
                output.append(f"  规则：{issue['rule']}")
                output.append(f"  描述：{issue['description']}")
        elif result["status"] == "FAIL":
            output.append("  未能获取具体问题详情，请检查验证器配置。")
        
        output.append(f"\n总结：{result['summary']}")
        
        return "\n".join(output)
