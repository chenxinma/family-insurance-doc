import textwrap
from pydantic_ai import Agent

from .reflector_agent import Reflection
from playbook import PlaybookOperator
from qwen_models import qwen

class CuratorAgent:
    """
    将Reflector提炼出的零散、原始的“教训”和“洞见”，系统化地整合并结构化为一个可持久化、易于检索和高效利用的“策略剧本”（Playbook）。
    """
    def __init__(self, playbook_operator: PlaybookOperator):
        # 初始化pydantic-ai Agent整编器
        self.agent = Agent(
            model=qwen("qwen-flash"),
            instructions=(
                textwrap.dedent("""
                你是一名严谨的知识库整编专家（Curator）。你的任务是根据反思器的分析，对策略剧本进行精准的增量更新以优化insurance_agent的执行效果。
                1.  **分析反思器输出**：仔细阅读反思器的分析结果，识别出需要更新的策略条目、新增的策略或修正的策略。
                2.  **新增或更新策略剧本**：根据分析结果，对策略剧本进行增量更新。确保更新后的剧本与反思器的分析一致，且符合策略剧本的格式规范。
                    可以使用`list_policies`和`read_policy`读取策略剧本，使用`create_policy`创建新策略条目，使用`modify_policy`和`delete_policy`修改或删除策略条目。
                3.  **关于insurance_agent**：
                    可以使用的工具：
                    - `grep` : ripgrepy搜索工具，搜索具体的保单文本

                策略剧本以ReAct格式组织，每个策略条目包含策略ID、策略名称和策略内容。
                策略剧本样例：
                ```
                # 目的：列出所有保单

                ## 思考（Reasoning）
                需要根据file map的信息提取关键信息，列出已知的所有保单。

                ## 行动步骤（Actions）
                ### 步骤1：按照file map的信息，列出所有已知的保单。

                ## 观察（Observation）
                完成步骤1后，我们将得到一份保险信息的清单。

                ## 总结（Summary）
                - 中荷人寿“互联网岁岁享2.0护理保险
                - 传世经典乐享2017终身寿险（分红型）
                - 平安平安福终身寿险（2016）
                我们成功地以条目形式列出所有已知保单。
                ```
                """)
            ),
            tools=[
                playbook_operator.read_policy,
                playbook_operator.create_policy,
                playbook_operator.modify_policy,
                playbook_operator.delete_policy,
                playbook_operator.list_policies
            ]
        )
    
    async def curate(self, objective: str, reflection: Reflection) -> str:
        """
        根据反思结果更新策略剧本
        """
        prompt = f"""
        目标：{objective}
        反思结果：{reflection.model_dump_json(ensure_ascii=False)}
        """
        result = await self.agent.run(prompt)
        return result.output
