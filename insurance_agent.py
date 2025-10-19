import json
from pathlib import Path
from pydantic_ai import Agent
import ripgrepy

from qwen_models import qwen

class InsuranceAgent:
    """
    InsuranceAgent类实现命令行问答功能
    """

    def __init__(self, map_file: str, docs_directory: str):
        self.map_file = Path(map_file)
        self.docs_directory = Path(docs_directory)
        
        # 加载map.json文件
        if self.map_file.exists():
            with open(self.map_file, 'r', encoding='utf-8') as f:
                self.file_map = json.load(f)
        else:
            self.file_map = {}
            
        # 初始化pydantic-ai Agent
        self.agent = Agent(
            model=qwen("qwen3-max"),
            instructions=(
                "You are an insurance expert agent. Your role is to answer questions about insurance policies "
                "based on the provided documents. You will use a ReAct (Reasoning + Action) approach to solve user queries.\n\n"
                "Here's how you should approach each question:\n"
                "1. **Thought**: Analyze the user's question and determine which documents might contain relevant information.\n"
                "2. **Action**: Use the `grep` tool to search for relevant information in specific document files.\n"
                "3. **Observation**: Examine the search results from grep to find the most relevant information.\n"
                "4. **Answer**: Provide a clear, accurate, and helpful response based on the information found.\n\n"
                "Use the file_map to locate relevant documents. The file_map contains document titles and their file paths.\n"
                "When using the grep tool, be specific with your search queries to find the most relevant information.\n"
                "If the initial grep results don't provide enough context, you can increase the context_lines parameter to get more surrounding lines.\n"
                "Always provide your final answer in a clear and concise manner.\n"
                f"Here is the file map: {self.file_map}\n\n"
                "Example interaction pattern:\n"
                "User: What is the coverage amount for the health insurance policy?\n"
                "Thought: I need to find information about health insurance coverage amounts. I'll look through the file_map to identify relevant documents.\n"
                "Action: grep(query='coverage amount', file_path='processed-docs/health_policy.txt', context_lines=10)\n"
                "Observation: [Results from grep showing relevant lines with more context]\n"
                "Answer: Based on the health insurance policy document, the coverage amount is $500,000.\n\n"
                "Remember to always follow this ReAct pattern for optimal results."
            ),
            tools=[self.grep], # 注册工具函数
        )


    def grep(self, query: str, file_path: str, context_lines: int = 5) -> str:
        """
        搜索相关内容

        Args:
            query (str): 搜索查询的ripgrep表达式
            file_path (str): 要搜索的文件路径
            context_lines (int, optional): 上下文行数，默认5行

        Returns:
            str: 搜索结果，包含匹配行的行号和内容
        """
        rg = ripgrepy.Ripgrepy(query, file_path)
        return rg.E("utf-8").C(context_lines).run().as_string
