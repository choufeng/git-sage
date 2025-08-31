from typing import Dict, Union, List
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

# Import new AI services
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    from .modelscope_wrapper import ModelScopeInferenceChatModel
except ImportError:
    ModelScopeInferenceChatModel = None

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
        elif language_model == "gemini":
            if ChatGoogleGenerativeAI is None:
                raise ValueError("Gemini support requires langchain-google-genai package. Install with: pip install langchain-google-genai")
            return ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=0.5
            )
        elif language_model == "modelscope":
            if ModelScopeInferenceChatModel is None:
                raise ValueError("ModelScope support is not available. Check modelscope_wrapper.py")
            return ModelScopeInferenceChatModel(
                model_name=model_name,
                api_key=api_key,
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
    
    def generate_pr_content(self, commits: List[Dict[str, str]], diff_content: str, ticket: str = None, no_verify: bool = False) -> Dict[str, str]:
        """
        Generate PR title and description based on commits and diff content
        
        Args:
            commits: List of commit information dictionaries
            diff_content: The git diff content between current branch and main branch
            ticket: Optional ticket number extracted from branch name
            
        Returns:
            Dict with 'title' and 'description' keys
        """
        try:
            language = self.config_manager.get_language()
            
            # Build commit summary
            commit_summary = ""
            if commits:
                commit_summary = "\n".join([f"- {commit['hash']}: {commit['message']}" for commit in commits])
            
            # Build system instruction
            system_instruction = f"""IMPORTANT: You MUST respond in {language} language.
For en: Use English only
For zh-CN: Use Simplified Chinese (简体中文) only
For zh-TW: Use Traditional Chinese (繁體中文) only

Your response format MUST be:
title: PR_TITLE
description: PR_DESCRIPTION

All text in the response MUST be in the specified language ({language}).
"""
            
            # Determine QA section content based on no_verify flag
            qa_instruction = "[QA: None]" if no_verify else """{{Based on code changes, determine:}}
- If there are UI changes or user-visible functionality changes: [QA: Verify] + provide simple verification steps
- If no UI changes (backend logic, refactoring, config, etc.): [QA: None]

QA Decision Rules:
- UI components, pages, styles, user interactions → [QA: Verify]
- API endpoints affecting frontend → [QA: Verify]  
- Pure backend logic, database changes, refactoring, config → [QA: None]
- Tests, docs, build scripts → [QA: None]"""
            
            prompt = f"""{system_instruction}

You are a professional software developer creating a Pull Request. Please analyze the following information and generate an appropriate PR title and description.

IMPORTANT: Follow these strict formatting rules for the PR title:
- Format: {{TYPE}}:[{{TICKET}}] {{DESCRIPTION}}
- TYPE should be one of: Feat, Fix, Update, Breaking, Docs, Chore, Test, Build, Refactor
- TICKET: Use the provided ticket number if available
- DESCRIPTION: Brief, clear description of the change

PR Description Requirements (MUST follow this exact three-section structure):

### Description
{{Brief summary of what this PR does (1-2 sentences)}}
- {{Detailed technical change 1}}
- {{Detailed technical change 2}}
- {{Detailed technical change 3}}
- {{Detailed technical change 4 (if needed)}}
- {{Detailed technical change 5 (if needed)}}

### Related issues or context
- https://compass-tech.atlassian.net/browse/{{TICKET}}

### QA
{qa_instruction}

Analysis Steps:
1. Read branch commit messages to understand development intent
2. Analyze code diff to confirm actual changes and impact scope
3. Determine the most appropriate PR type
4. Decide QA section based on whether changes are user-visible
5. Generate description following the three-section structure

Branch Commits Information:
{commit_summary if commit_summary else "No commits found"}

Ticket Number: {ticket if ticket else "No ticket found"}

Code Diff Content:
{diff_content if diff_content else "No diff content available"}

Remember: Your ENTIRE response MUST be in {language} language as specified above.
IMPORTANT: You MUST follow the exact three-section format shown above.
"""
            
            # Call language model
            response = self._call_language_model(prompt)
            
            # Parse response to extract title and description
            lines = response.strip().split('\n')
            result = {'title': '', 'description': ''}
            
            # Find title
            for line in lines:
                if line.strip().lower().startswith('title:'):
                    result['title'] = line.strip()[6:].strip()
                    break
            
            # Extract description (everything after title line)
            description_lines = []
            title_found = False
            
            for line in lines:
                if line.strip().lower().startswith('title:'):
                    title_found = True
                    continue
                
                if title_found:
                    # Skip empty lines at the beginning
                    if not description_lines and not line.strip():
                        continue
                    description_lines.append(line)
            
            # Process description to handle the three-section format
            description_content = '\n'.join(description_lines).strip()
            
            # If the response doesn't start with ### Description, add it
            if description_content and not description_content.startswith('###'):
                # Try to find where the actual description content starts
                if 'description:' in description_content.lower():
                    # Remove "description:" prefix if present
                    desc_start = description_content.lower().find('description:')
                    description_content = description_content[desc_start + 12:].strip()
            
            result['description'] = description_content
            
            # Set defaults if missing
            if not result['title']:
                pr_type = self._determine_pr_type(commits, diff_content)
                ticket_part = f"[{ticket}] " if ticket else ""
                result['title'] = f"{pr_type}:{ticket_part}Update codebase"
            
            if not result['description']:
                # Generate default three-section description
                ticket_link = f"- https://compass-tech.atlassian.net/browse/{ticket}" if ticket else "- No related ticket"
                qa_section = "[QA: None]" if no_verify else "[QA: Verify]"
                result['description'] = f"""### Description
Update codebase with latest changes.
- Implement code improvements and modifications
- Update existing functionality

### Related issues or context
{ticket_link}

### QA
{qa_section}"""
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to generate PR content: {str(e)}") from e
    
    def _determine_pr_type(self, commits: List[Dict[str, str]], diff_content: str) -> str:
        """Determine PR type based on commits and diff content"""
        if not commits and not diff_content:
            return "Chore"
        
        # Check commit messages for common patterns
        if commits:
            commit_text = ' '.join([commit['message'].lower() for commit in commits])
            if 'feat' in commit_text or 'feature' in commit_text or 'add' in commit_text:
                return "Feat"
            elif 'fix' in commit_text or 'bug' in commit_text:
                return "Fix"
            elif 'update' in commit_text or 'improve' in commit_text:
                return "Update"
            elif 'break' in commit_text or 'breaking' in commit_text:
                return "Breaking"
            elif 'doc' in commit_text or 'readme' in commit_text:
                return "Docs"
            elif 'test' in commit_text:
                return "Test"
            elif 'build' in commit_text or 'config' in commit_text:
                return "Build"
            elif 'refactor' in commit_text:
                return "Refactor"
        
        # Default to Update if can't determine
        return "Update"