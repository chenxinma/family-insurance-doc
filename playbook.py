import os
from functools import wraps
from typing import Literal

from pydantic import BaseModel, Field
import ripgrepy

PLAYBOOK_DIR = './playbook'
LIST_FILE = os.path.join(PLAYBOOK_DIR, 'playbook-list.txt')

class Playbook(BaseModel):
    bullet_id: int = Field(description="策略文件序号")
    content: str = Field(description="策略文件内容")

class PlaybookEvaluation(BaseModel):
    bullet_id: int = Field(description="策略文件序号")
    impact: Literal["helpful", "harmful", "neutral"] = Field(description="对策略文件的评估")

class PlaybookOperator:
    @staticmethod
    def ensure_playbook_dir():
        """确保playbook目录存在的装饰器"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 确保目录存在的逻辑
                if not os.path.exists(PLAYBOOK_DIR):
                    os.makedirs(PLAYBOOK_DIR)
                # 调用原始函数
                return func(*args, **kwargs)
            return wrapper
        return decorator

    @ensure_playbook_dir()
    def create(self, content: str) -> int:
        """创建策略文件"""
        """新建策略文件"""
        bullet_id = self.get_next_bullet_id()
        filename = os.path.join(PLAYBOOK_DIR, f'{bullet_id:08d}.txt')
        with open(filename, 'w') as f:
            f.write(content)
        return self.get_next_bullet_id()

    @ensure_playbook_dir()
    def get_existing_indices(self) -> list[int]:
        """获取所有存在的策略文件序号"""
        indices = []
        if os.path.exists(LIST_FILE):
            with open(LIST_FILE, 'r') as f:
                for line in f:
                    try:
                        bullet_id = int(line.strip())
                        indices.append(bullet_id)
                    except ValueError:
                        continue
        return sorted(indices)
    
    @ensure_playbook_dir()
    def update_playbook_list(self):
        """更新playbook-list.txt文件"""
        indices = []
        for filename in os.listdir(PLAYBOOK_DIR):
            if filename.endswith('.txt') and filename[:-4].isdigit() and len(filename[:-4]) == 8:
                try:
                    bullet_id = int(filename[:-4])
                    indices.append(bullet_id)
                except ValueError:
                    continue
        indices.sort()
        with open(LIST_FILE, 'w') as f:
            for bullet_id in indices:
                f.write(str(bullet_id) + '\n')

    def get_next_bullet_id(self):
        """获取下一个可用的序号"""
        indices = self.get_existing_indices()
        if not indices:
            return 1
        return max(indices) + 1

    @ensure_playbook_dir()
    def read_policy(self, bullet_id:int):
        """读取策略文件内容"""
        filename = os.path.join(PLAYBOOK_DIR, f'{bullet_id:08d}.txt')
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return f.read()
        return None

    @ensure_playbook_dir()
    def modify_policy(self, bullet_id:int, content: str):
        """修改策略文件内容"""
        filename = os.path.join(PLAYBOOK_DIR, f'{bullet_id:08d}.txt')
        if os.path.exists(filename):
            with open(filename, 'w') as f:
                f.write(content)
            self.update_playbook_list()
            return True
        return False

    @ensure_playbook_dir()
    def delete_policy(self, bullet_id:int):
        """删除策略文件"""
        filename = os.path.join(PLAYBOOK_DIR, f'{bullet_id:08d}.txt')
        if os.path.exists(filename):
            os.remove(filename)
            self.update_playbook_list()
            return True
        return False
    
    @ensure_playbook_dir()
    def list_policies(self) -> list[Playbook]:
        """列出所有策略文件"""
        indices = self.get_existing_indices()
        policies = []
        for bullet_id in indices:
            content = self.read_policy(bullet_id)
            if content is not None:
                policies.append(Playbook(bullet_id=bullet_id, content=content))
        return policies
    
    @ensure_playbook_dir()
    def grep(self, query: str, context_lines: int = 5) -> list[Playbook]:
        """
        搜索相关内容

        Args:
            query (str): 搜索查询的ripgrep表达式
            context_lines (int, optional): 上下文行数，默认5行
    
        Returns:
            list[Playbook]: 包含匹配行的Playbook对象列表
        """
        policies = []
        if len(self.get_existing_indices()) == 0:
            return policies
        
        rg = ripgrepy.Ripgrepy(query, PLAYBOOK_DIR + "/*.txt")
        for item in rg.E("utf-8").C(context_lines).json().run().as_dict:
            bullet_id = int(os.path.basename(item['path'])[:-4])
            policies.append(Playbook(bullet_id=bullet_id, content=item["line"]['text']))
        
        return policies
