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
        """设置Ollama实例"""
        return OllamaLLM(
            model=self.config_manager.get_model(),
            base_url=self.config_manager.get_model_endpoint()
        )
    
    def _call_language_model(self, prompt: str) -> str:
        """调用语言模型服务"""
        try:
            prompt_template = ChatPromptTemplate.from_template("{input}")
            output_parser = StrOutputParser()
            chain = prompt_template | self.model | output_parser
            response = chain.invoke({"input": prompt})
            return response
        except Exception as e:
            raise Exception(f"Failed to call language model: {e}") from e
    
    def _create_workflow(self) -> Graph:
        """创建LangGraph工作流"""
        
        # 定义节点函数
        def analyze_diff(state):
            """分析git diff内容"""
            diff_content = state["diff_content"]
            language = self.config_manager.get_language()
            
            prompt = f"""Please analyze the following git diff content and provide a response in {language} language:

            {diff_content}

            Please provide a concise commit message in the following format:
            type: main type of change (feat/fix/docs/style/refactor/test/chore)
            subject: brief description of changes (no more than 50 characters)
            body: detailed explanation of changes

            Please ensure the response follows this exact format, but use {language} language for all descriptions:
            type: feat
            subject: [your subject in {language}]
            body: [your detailed explanation in {language}]
            """
            
            # 调用语言模型获取分析结果
            response = self._call_language_model(prompt)
            
            # 解析响应
            lines = response.strip().split('\n')
            analysis = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    if key in ['type', 'subject', 'body']:
                        analysis[key] = value
            
            # 确保所有必需字段都存在
            if not all(key in analysis for key in ['type', 'subject', 'body']):
                raise Exception("Invalid AI response format")
            
            return {
                **state,
                "analysis": analysis
            }
        
        def format_message(state):
            """格式化提交信息"""
            analysis = state["analysis"]
            return {
                **state,
                "commit_message": f"{analysis['type']}: {analysis['subject']}\n\n{analysis['body']}"
            }
        
        # 创建工作流图
        workflow = Graph()
        
        # 添加节点
        workflow.add_node("analyze_diff", analyze_diff)
        workflow.add_node("format_message", format_message)
        
        # 设置边
        workflow.add_edge("analyze_diff", "format_message")
        
        # 设置入口和出口
        workflow.set_entry_point("analyze_diff")
        workflow.set_finish_point("format_message")
        
        return workflow.compile()
    
    def process_diff(self, diff_content: str) -> str:
        """处理git diff内容并生成提交信息"""
        try:
            # 运行工作流
            result = self.workflow.invoke({
                "diff_content": diff_content
            })
            
            return result["commit_message"]
        except Exception as e:
            raise Exception(f"Failed to process diff: {e}") from e
