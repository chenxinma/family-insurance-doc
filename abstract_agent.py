import json
import asyncio
import textwrap
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic_ai import Agent
from tqdm import tqdm

from qwen_models import qwen


class AbstractAgent:
    """
    AbstractAgent类实现对processed-docs下的txt文件做摘要，并更新到map.json
    """

    def __init__(self, map_file: str, docs_directory: str, chunk_lines:int=200):
        self.map_file = Path(map_file)
        self.docs_directory = Path(docs_directory)
        self.chunk_lines = chunk_lines
        # 摘要完成文件记录路径
        self.completed_docs_file = self.docs_directory / "docs.wraped"
        
        # 加载map.json文件
        if self.map_file.exists():
            with open(self.map_file, 'r', encoding='utf-8') as f:
                self.file_map = json.load(f)
        else:
            self.file_map = {}
            
        # 初始化已完成摘要的文件记录
        self.completed_docs = set()
        if self.completed_docs_file.exists():
            with open(self.completed_docs_file, 'r', encoding='utf-8') as f:
                for line in f:
                    self.completed_docs.add(line.strip())
            
        # 初始化pydantic-ai Agent用于摘要
        self.agent = Agent(
            model=qwen("qwen-flash"),
            instructions=(
                textwrap.dedent("""
                你是一个专业的法律合同摘要员，负责对保险合同文件进行摘要。
                保险合同文件通常包括投保人、被保险人、保险产品、保险金额、保险时间、保险条款等内容。
                摘要时需要保留关键信息，同时保持摘要的清晰度和易读性。
                摘要的长度在300字左右。
                摘要的内容包括
                - 投保人
                - 被保险人
                - 保险产品
                - 保险金额
                - 保费金额
                - 保费缴费时间
                - 保险到期时间
                - 保险条款
                """)
            ),
        )

    async def summarize_document(self, file_path: Path) -> str:
        """
        对单个文档进行摘要
        """
        # 文本预处理：读取文件内容，去除多余空白，统一每行长度为100字
        processed_file_path = file_path.with_suffix('.wrap')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 去除多余的空白行和空格
        lines = content.splitlines()
        stripped_lines = [line.strip() for line in lines if line.strip()]
        cleaned_content = '\n'.join(stripped_lines)
        
        # 使用textwrap.wrap将每行长度统一成100字
        wrapped_lines = textwrap.wrap(cleaned_content, width=100)
        
        # 保存处理后的内容到新文件
        with open(processed_file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(wrapped_lines))
        
        # 读取处理后的文件内容，分片处理
        with open(processed_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        abstract = ""
        # 计算总chunk数用于进度条
        total_chunks = (len(lines) + 99) // 100  # 向上取整
        
        # 创建进度条
        pbar = tqdm(
            total=total_chunks,
            desc=f"处理 {file_path.name}",
            unit="chunk",
            leave=False
        )
        
        try:
            # 每次读取self.chunk_lines行
            for i in range(0, len(lines), self.chunk_lines):
                chunk = ''.join(lines[i:i+self.chunk_lines])
                _content = f"已经总结的摘要：{abstract}\n 新的内容：{chunk}"
                result = await self.agent.run(_content)
                abstract = result.output
                # 更新进度条
                pbar.update(1)
        finally:
            # 确保进度条关闭
            pbar.close()
            # 删除临时的.wrap文件，释放内存
            if processed_file_path.exists():
                processed_file_path.unlink()
   
        return abstract

    async def process_all_documents(self):
        """
        处理所有文档并更新map.json
        """
        # 过滤出存在的文档
        valid_docs = [(title, info) for title, info in self.file_map.items() 
                     if Path(info["txt_path"]).exists() and info["sha1_hash"] not in self.completed_docs]
        
        if not valid_docs:
            print("没有找到有效的文档需要处理")
            return
            
        # 创建总体进度条
        overall_pbar = tqdm(
            total=len(valid_docs),
            desc="总体进度",
            unit="doc"
        )
        
        tasks = []
        for title, info in valid_docs:
            txt_path = Path(info["txt_path"])
            # 创建异步任务来处理每个文档，并传递进度条
            task = asyncio.create_task(self._process_single_document(title, txt_path, info["sha1_hash"], overall_pbar))
            tasks.append(task)
        
        try:
            # 等待所有任务完成
            await asyncio.gather(*tasks)
        finally:
            # 确保进度条关闭
            overall_pbar.close()
        
        # 保存已完成摘要的文件记录
        with open(self.completed_docs_file, 'w', encoding='utf-8') as f:
            for sha1_hash in self.completed_docs:
                f.write(f"{sha1_hash}\n")
        
        # 保存更新后的map.json
        with open(self.map_file, 'w', encoding='utf-8') as f:
            json.dump(self.file_map, f, ensure_ascii=False, indent=2)
        print("\n所有文档摘要更新完成")

    async def _process_single_document(self, title: str, txt_path: Path, sha1_hash: str, pbar: Optional[tqdm] = None):
        """
        处理单个文档
        """
        print(f"正在处理文档: {title}")
        try:
            abstract = await self.summarize_document(txt_path)
            self.file_map[title]["abstract"] = abstract
            # 记录已完成摘要的文件
            self.completed_docs.add(sha1_hash)
            print(f"文档 {title} 摘要生成完成")
        except Exception as e:
            print(f"处理文档 {title} 时出错: {e}")
        finally:
            # 更新总体进度条
            if pbar:
                pbar.update(1)


# 如果需要直接运行这个模块
if __name__ == "__main__":
    # 这部分代码需要在main.py中调用
    pass