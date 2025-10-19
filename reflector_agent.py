import textwrap
from typing import Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent, Tool
from pydantic_ai.messages import ModelMessage
from qwen_models import qwen
from playbook import PlaybookOperator

playbook_operator = PlaybookOperator()

class Reflection(BaseModel):
    reasoning: str = Field(description="反思的推理链条")
    error_identification: Optional[str] = Field(description="反思中识别到的错误", default=None)
    root_cause_analysis: Optional[str] = Field(description="反思中识别到的根因分析", default=None)
    correct_approach: Optional[str] = Field(description="反思中识别到的正确方法", default=None)
    key_insight: Optional[str] = Field(description="反思中识别到的关键洞察", default=None)
    playbook_evaluation: Optional[list[dict]] = Field(description="反思中对Playbook条目的评估", default=None)

class ReflectorAgent:
    """
    ReflectorAgent类实现AI的反思
    """
    def __init__(self):
        # 初始化pydantic-ai Agent用于反思
        self.agent = Agent(
            model=qwen("qwen-flash"),
            output_type=Reflection,
            instructions=(
                textwrap.dedent("""
                你是一名资深的Insurance Agent智能体行为诊断专家。你的核心任务是深入分析智能体的执行轨迹，准确诊断其成功或失败的原因，并提炼出可复用的策略和教训。
                可以通过playbook_grep工具搜索Playbook中相关的策略条目。
                **分析要求：**
                1.  **逐步复盘**：仔细检查执行轨迹中的每一步，思考其意图和实际效果。
                2.  **定位关键点**：识别出直接导致成功或失败的关键决策、工具调用或逻辑判断。
                3.  **归因分析**：判断问题是源于对API的误解、策略选择不当、逻辑错误，还是忽略了Playbook中的某条重要建议。
                4.  **提炼新知**：从本次经历中总结出新的、有价值的策略、常见陷阱或优化技巧。
                """)
            ),
            tools=[
                Tool(
                    function=playbook_operator.grep,
                    name="playbook_grep",
                    description="搜索Playbook中相关的策略条目",
                )
            ]
        )

    async def reflect(self, messages: list[ModelMessage]) -> Reflection:
        """
        反思智能体的执行轨迹，返回反思结果
        """
        # 构建反思提示
        # 调用pydantic-ai Agent进行反思
        response = await self.agent.run(message_history=messages)
        return response.output