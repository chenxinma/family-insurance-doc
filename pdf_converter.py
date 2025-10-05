import pdfplumber
import json
import hashlib
from pathlib import Path


class PDFToTxtConverter:
    """
    PDFToTxtConverter类封装pdf文本提取相关功能
    """

    def __init__(self, pdf_directory: str, output_directory: str, map_file: str):
        self.pdf_directory = Path(pdf_directory)
        self.output_directory = Path(output_directory)
        self.map_file = Path(map_file)
        self.pdf_files = list(self.pdf_directory.glob("*.pdf"))
        
        # 确保输出目录存在
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
        # 初始化或加载map.json
        if self.map_file.exists():
            with open(self.map_file, 'r', encoding='utf-8') as f:
                self.file_map = json.load(f)
        else:
            self.file_map = {}

    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        从PDF文件中提取文本
        """
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""  # 处理可能的None值
        return text

    def convert_pdf_to_txt(self, pdf_path: Path) -> Path:
        """
        将PDF文件转换为TXT文件
        """
        txt_filename = pdf_path.stem + ".txt"
        txt_path = self.output_directory / txt_filename
        
        text = self.extract_text_from_pdf(pdf_path)
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
            
        return txt_path

    def calculate_sha1(self, file_path: Path) -> str:
        """
        计算文件的SHA1哈希值
        """
        sha1_hash = hashlib.sha1()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha1_hash.update(chunk)
        return sha1_hash.hexdigest()

    def update_map_file(self, pdf_path: Path, txt_path: Path, pdf_sha1: str):
        """
        更新map.json文件，记录txt文件路径、标题、摘要和SHA1哈希值
        """
        
        # 这里简化处理，实际项目中可能需要更复杂的标题和摘要提取逻辑
        title = pdf_path.stem
        # 摘要可以是文档的前几行或其他逻辑提取的内容
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 取前100个字符作为摘要示例
            abstract = content[:100] if len(content) > 100 else content
            
        self.file_map[title] = {
            "txt_path": str(txt_path.relative_to(self.output_directory.parent)),
            "title": title,
            "abstract": abstract,
            "sha1_hash": pdf_sha1
        }
        
        with open(self.map_file, 'w', encoding='utf-8') as f:
            json.dump(self.file_map, f, ensure_ascii=False, indent=2)


    def process_all_pdfs(self):
        """
        处理所有PDF文件
        """
        for pdf_file in self.pdf_files:
            print(f"Processing {pdf_file.name}...")
            # 计算PDF文件的SHA1哈希值
            pdf_sha1 = self.calculate_sha1(pdf_file)

            # 检查是否已经处理过相同内容的文件
            if len([entry for entry in self.file_map.values() if entry.get("sha1_hash") == pdf_sha1]) > 0:
                print(f"Skipping {pdf_file} as it has the same content as a previously processed file")
                continue

            # 处理pdf文件
            txt_path = self.output_directory / (pdf_file.stem + ".txt")
            txt_path = self.convert_pdf_to_txt(pdf_file)   
            self.update_map_file(pdf_file, txt_path, pdf_sha1)
            print(f"Finished processing {pdf_file.name}")

        