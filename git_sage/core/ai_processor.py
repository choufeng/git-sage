from typing import Dict, Union
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

class AIProcessor:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.model = self._setup_model()
    
    def _setup_model(self) -> Union[OllamaLLM, ChatOpenAI]:
        """Setup language model based on configuration"""
        language_model = self.config_manager.get_language_model()
        model_name = self.config_manager.get_model()
        endpoint = self.config_manager.get_model_endpoint()
        api_key = self.config_manager.get_api_key()
        
        print(f"Setting up model: {language_model} ({model_name}) at {endpoint}")
        
        if language_model == "ollama":
            os.environ["OLLAMA_BASE_URL"] = endpoint
            return OllamaLLM(
                model=model_name,
                base_url=endpoint,
                temperature=0.5
            )
        elif language_model == "openrouter":
            return ChatOpenAI(
                model=model_name,
                openai_api_key=api_key,
                base_url=endpoint,
                temperature=0.5,
                default_headers={
                    "HTTP-Referer": "git-sage-cli",
                    "X-Title": "Git-Sage"
                }
            )
        elif language_model == "deepseek":
            return ChatOpenAI(
                model=model_name,
                openai_api_key=api_key,
                base_url=endpoint,
                temperature=0.5
            )
        else:
            raise ValueError(f"Unsupported language model service: {language_model}")
    
    def _call_language_model(self, prompt: str) -> str:
        """Call language model service"""
        try:
            prompt_template = ChatPromptTemplate.from_template("{input}")
            output_parser = StrOutputParser()
            chain = prompt_template | self.model | output_parser
            
            print("Calling language model...")
            response = chain.invoke({"input": prompt})
            return response
        except Exception as e:
            raise Exception(f"Failed to call language model: {str(e)}") from e
    
    def _parse_response(self, response: str) -> Dict[str, str]:
        """Parse AI response"""
        lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
        analysis = {}
        body_lines = []
        in_body = False
        
        for line in lines:
            if ':' in line:
                key, value = [part.strip() for part in line.split(':', 1)]
                key = key.lower()
                
                if key == 'type' and not analysis.get('type'):
                    analysis['type'] = value
                elif key == 'subject' and not analysis.get('subject'):
                    analysis['subject'] = value
                elif key == 'body':
                    in_body = True
                    if value:
                        body_lines.append(value)
            elif in_body:
                body_lines.append(line)
        
        if body_lines:
            # 处理body部分，保持列表项的换行格式
            formatted_body = []
            for line in body_lines:
                if line.startswith('- '):
                    # 如果是列表项，确保前后有换行
                    if formatted_body and not formatted_body[-1].endswith('\n'):
                        formatted_body.append('\n')
                    formatted_body.append(line + '\n')
                else:
                    formatted_body.append(line + ' ')
            
            analysis['body'] = ''.join(formatted_body).strip()
        
        # Set defaults if missing
        if 'type' not in analysis:
            analysis['type'] = 'docs'  # Default to docs type
        if 'subject' not in analysis:
            analysis['subject'] = 'Update documentation'  # Default subject
        if 'body' not in analysis:
            analysis['body'] = 'Update project documentation and improve clarity.'  # Default body
            
        return analysis
    
    def _clean_response(self, response: str) -> str:
        """Clean the response by removing markdown code blocks and other formatting."""
        # Remove markdown code block markers
        response = response.replace('```json', '').replace('```', '').strip()
        
        # Remove any leading/trailing whitespace
        response = response.strip()
        
        return response

    def _ensure_json_response(self, prompt: str) -> str:
        """Ensure the response is in valid JSON format."""
        system_prompt = """你是一个代码审查助手。请直接返回JSON格式的响应，不要添加markdown格式。
确保响应包含以下字段：
- status: "PASS" 或 "FAIL"
- issues: 问题列表，每个问题包含 file、line、rule 和 description
- summary: 总体评估总结

即使没有发现问题，也要返回完整的 JSON 结构。
注意：请直接返回 JSON，不要添加 ```json 或其他格式标记。"""
        
        full_prompt = f"{system_prompt}\n\n{prompt}"
        response = self._call_language_model(full_prompt)
        return self._clean_response(response)

    def get_response(self, prompt: str) -> str:
        """Get response from language model"""
        try:
            return self._call_language_model(prompt)
        except Exception as e:
            raise Exception(f"Failed to get response: {str(e)}") from e

    def process_diff(self, diff_content: str) -> str:
        """Process git diff content and generate commit message"""
        try:
            language = self.config_manager.get_language()
            
            # 构建系统角色指令
            system_instruction = f"""IMPORTANT: You MUST respond in {language} language.
For en: Use English only
For zh-CN: Use Simplified Chinese (简体中文) only
For zh-TW: Use Traditional Chinese (繁體中文) only

Your response format MUST be:
type: tag
subject: brief description
body: detailed explanation
    - bullet point 1
    - bullet point 2
    ...

All text in the response (including type, subject, and body) MUST be in the specified language ({language}).
"""
            
            prompt = f"""{system_instruction}

You are a professional code reviewer and commit message generator. Please carefully analyze the following git diff content and generate a structured commit message. Follow this thought process:

1. Initial Understanding Phase
- Quick overview of the entire diff to form a general impression
- Identify main modified files and modules
- Consider the potential purpose and impact of these changes

2. Deep Analysis Phase
- Detailed examination of each code change
- Analyze technical characteristics of changes (new features, bug fixes, refactoring, etc.)
- Consider the impact level of these changes on the system
- Think about backward compatibility implications

3. Multi-dimensional Evaluation
- Functional Perspective: What new features are implemented or what issues are fixed?
- Maintainability Perspective: Is code quality improved? Is technical debt addressed?
- Compatibility Perspective: Are there any breaking changes?

4. Verification and Summary
- Double-check if all changes are correctly understood
- Confirm if the chosen change type tag is most accurate
- Verify if the description completely and accurately reflects the essence of changes

IMPORTANT WRITING STYLE:
Write commit messages in an active, direct style. Avoid self-referential phrases like "this commit", "this change", "this update", "this modification". Instead, describe what the change does directly using imperative mood.

Examples:
- Bad: "This commit adds user authentication"
- Good: "Add user authentication"
- Bad: "This change fixes a bug in user login" 
- Good: "Fix user login validation issue"
- Bad: "This update improves performance"
- Good: "Improve database query performance"

Commit Tags Explanation:

Patch Version (PATCH) Tags:
- fix: For bug fixes
- build: For build process changes only
- maint: For small maintenance tasks like technical debt cleanup, refactoring, and non-breaking dependency updates
- test: For application end-to-end tests
- patch: Generic patch tag when other patch tags don't apply

Minor Version (MINOR) Tags:
- feat: For implementing new features
- minor: Generic minor tag when other minor tags don't apply
- update: For backward-compatible enhancements to existing features

Major Version (MAJOR) Tags:
- breaking: For backward-incompatible enhancements or features
- major: Generic major tag when other major tags don't apply

No Version Update (NO-OP) Tags:
- docs: For documentation changes only
- chore: For other changes that don't affect the actual environment (code comments, non-package files, unit tests)

The diff content is:

{diff_content}

Remember: Your ENTIRE response MUST be in {language} language as specified above.
"""
            
            # Call language model to get analysis result
            response = self._call_language_model(prompt)
            
            # Parse response
            analysis = self._parse_response(response)
            
            # Format commit message
            commit_message = f"{analysis['type']}: {analysis['subject']}\n\n{analysis['body']}"
            print(f"\nGenerated commit message:\n{commit_message}")
            
            return commit_message
            
        except Exception as e:
            raise Exception(f"Failed to process diff: {str(e)}") from e

    def analyze_code(self, prompt: str, diff_content: str) -> str:
        """
        Analyze code changes using AI.
        
        Args:
            prompt: The prompt containing rules and instructions
            diff_content: The git diff content to analyze
            
        Returns:
            str: JSON formatted analysis result
        """
        # Combine the prompt with the diff content
        full_prompt = f"{prompt}\n\n这是要分析的代码变更：\n\n{diff_content}"
        
        # Get AI response using JSON-specific method
        return self._ensure_json_response(full_prompt)
