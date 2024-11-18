from typing import Dict
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

class AIProcessor:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        os.environ["OLLAMA_BASE_URL"] = self.config_manager.get_model_endpoint()
        self.model = self._setup_model()
    
    def _setup_model(self) -> OllamaLLM:
        """Setup Ollama instance"""
        return OllamaLLM(
            model=self.config_manager.get_model(),
            base_url=self.config_manager.get_model_endpoint()
        )
    
    def _call_language_model(self, prompt: str) -> str:
        """Call language model service"""
        try:
            prompt_template = ChatPromptTemplate.from_template("{input}")
            output_parser = StrOutputParser()
            chain = prompt_template | self.model | output_parser
            response = chain.invoke({"input": prompt})
            return response
        except Exception as e:
            raise Exception(f"Failed to call language model: {e}") from e
    
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
            
            prompt = f"""You are a commit message generator. Analyze the following git diff and generate a structured commit message in {language}. Focus only on describing the actual changes shown in the diff, not any potential follow-up actions.

The diff content is:

{diff_content}

You must respond in exactly this format:
type: [choose one: feat/fix/docs/style/refactor/test/chore]
subject: [brief description, max 50 chars]
body: [detailed explanation of the changes shown in the diff]

Example of good format:
type: docs
subject: Update README with project features
body: Convert README to English and improve documentation structure. Add detailed feature list and installation instructions. Include language support information.

Remember:
1. Keep the format exactly as shown
2. Use {language} for all text
3. Choose type from the given options
4. Keep subject under 50 characters
5. Only describe changes shown in the diff
6. Do not include any installation steps or commands in the message

Your response:"""
            
            # Call language model to get analysis result
            response = self._call_language_model(prompt)
            
            # Parse response
            analysis = self._parse_response(response)
            
            # Format commit message
            return f"{analysis['type']}: {analysis['subject']}\n\n{analysis['body']}"
            
        except Exception as e:
            raise Exception(f"Failed to process diff: {e}") from e
