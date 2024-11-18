from typing import Dict, List
from langgraph.graph import Graph
from langgraph.prebuilt import ToolExecutor
from operator import itemgetter
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class AIProcessor:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.workflow = self._create_workflow()
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
    
    def _create_workflow(self) -> Graph:
        """Create LangGraph workflow"""
        
        # Define node functions
        def analyze_diff(state):
            """Analyze git diff content"""
            diff_content = state["diff_content"]
            language = self.config_manager.get_language()
            
            prompt = f"""You are a commit message generator. Please analyze the following git diff content and generate a standardized commit message.

IMPORTANT INSTRUCTIONS:
1. Generate the commit message in {language} language
2. Return EXACTLY three lines in the specified format
3. Each line must start with the specified prefix
4. Use a commit type from the provided list
5. Keep subject under 50 characters
6. Do not add any extra lines or explanations

Changes to analyze:
{diff_content}

Available commit types (grouped by version impact):

PATCH version tags:
- Fix (for bug fixes)
- Build (changes to build process)
- Maint or Maintenance (maintenance tasks)
- Test (for e2e tests)
- Patch (other patch-level changes)

MINOR version tags:
- Feat or Feature or New (new features)
- Minor (other minor version changes)
- Update (backwards-compatible enhancements)

MAJOR version tags:
- Breaking (backwards-incompatible changes)
- Major (other major version changes)

NO-OP tags:
- Docs (documentation only)
- Chore (comments, unit tests, etc.)

REQUIRED OUTPUT FORMAT:
type: <select one type from above>
subject: <brief description>
body: <detailed explanation>

Example output:
type: feat
subject: Add user authentication
body: Implemented JWT-based user authentication system with login, registration, and password reset"""
            
            # Call language model
            response = self._call_language_model(prompt)
            
            # Parse response
            try:
                lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
                
                # Ensure exactly three lines
                if len(lines) != 3:
                    raise Exception(f"Expected 3 lines, got {len(lines)}")
                
                # Parse each line
                analysis = {}
                required_prefixes = ['type:', 'subject:', 'body:']
                
                for line, prefix in zip(lines, required_prefixes):
                    if not line.lower().startswith(prefix):
                        raise Exception(f"Line must start with '{prefix}': {line}")
                    key = prefix[:-1]  # remove colon
                    value = line[len(prefix):].strip()
                    analysis[key] = value
                
                # Validate commit type
                valid_types = ['fix', 'build', 'maint', 'maintenance', 'test', 'patch',
                             'feat', 'feature', 'new', 'minor', 'update',
                             'breaking', 'major',
                             'docs', 'chore']
                
                if analysis['type'].lower() not in valid_types:
                    raise Exception(f"Invalid type: {analysis['type']}")
                
                # Validate subject length
                if len(analysis['subject']) > 50:
                    raise Exception("Subject exceeds 50 characters")
                
                return {
                    **state,
                    "analysis": analysis
                }
            except Exception as e:
                raise Exception(f"Failed to parse AI response: {str(e)}\nResponse was:\n{response}")
        
        def format_message(state):
            """Format commit message"""
            analysis = state["analysis"]
            return {
                **state,
                "commit_message": f"{analysis['type']}: {analysis['subject']}\n\n{analysis['body']}"
            }
        
        # Create workflow graph
        workflow = Graph()
        
        # Add nodes
        workflow.add_node("analyze_diff", analyze_diff)
        workflow.add_node("format_message", format_message)
        
        # Set edges
        workflow.add_edge("analyze_diff", "format_message")
        
        # Set entry and exit points
        workflow.set_entry_point("analyze_diff")
        workflow.set_finish_point("format_message")
        
        return workflow.compile()
    
    def process_diff(self, diff_content: str) -> str:
        """Process git diff content and generate commit message"""
        try:
            # Run workflow
            result = self.workflow.invoke({
                "diff_content": diff_content
            })
            
            return result["commit_message"]
        except Exception as e:
            raise Exception(f"Failed to process diff: {e}") from e
