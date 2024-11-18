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
                base_url=endpoint
            )
        elif language_model == "openrouter":
            return ChatOpenAI(
                model=model_name,
                openai_api_key=api_key,
                base_url=endpoint,
                default_headers={
                    "HTTP-Referer": "git-sage-cli",
                    "X-Title": "Git-Sage"
                }
            )
        elif language_model == "deepseek":
            return ChatOpenAI(
                model=model_name,
                openai_api_key=api_key,
                base_url=endpoint
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
            analysis['body'] = ' '.join(body_lines)
        
        # Set defaults if missing
        if 'type' not in analysis:
            analysis['type'] = 'docs'  # Default to docs type
        if 'subject' not in analysis:
            analysis['subject'] = 'Update documentation'  # Default subject
        if 'body' not in analysis:
            analysis['body'] = 'Update project documentation and improve clarity.'  # Default body
            
        return analysis
    
    def process_diff(self, diff_content: str) -> str:
        """Process git diff content and generate commit message"""
        try:
            language = self.config_manager.get_language()
            
            prompt = f"""You are a professional code reviewer and commit message generator. Please carefully analyze the following git diff content and generate a structured commit message. Follow this thought process:

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

Language requirement: {language} (en for English, zh for Chinese)

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

You must respond in exactly this format:
type: [choose the most appropriate tag from the above list]
subject: [brief description, max 50 chars]
body: [detailed explanation of the changes]

Example of good format:
type: docs
subject: Update README with project features
body: Convert README to English and improve documentation structure. Add detailed feature list and installation instructions. Include language support information.

Remember:
1. Keep the format exactly as shown
2. Use {language} for all text (en for English, zh for Chinese)
3. Choose type from the given tag options based on the nature of changes
4. Keep subject under 50 characters
5. Only describe changes shown in the diff
6. Do not include any installation steps or commands in the message
7. Choose the most specific and appropriate tag for the changes

Begin your analysis:"""
            
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
