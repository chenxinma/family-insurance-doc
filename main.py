
import argparse
import asyncio
from pathlib import Path

from pdf_converter import PDFToTxtConverter
from insurance_agent import InsuranceAgent


def main():
    parser = argparse.ArgumentParser(description="家庭保险文档处理工具")
    parser.add_argument(
        "--convert", 
        action="store_true", 
        help="将PDF文件转换为TXT并更新map.json"
    )
    parser.add_argument(
        "--question", 
        action="store_true", 
        help="向保险文档提问"
    )
    
    args = parser.parse_args()
    
    # 定义路径
    pdf_directory = "insurance-docs"
    output_directory = "processed-docs"
    map_file = "map.json"
    
    if args.convert:
        # 创建PDF转换器并处理所有PDF文件
        converter = PDFToTxtConverter(pdf_directory, output_directory, map_file)
        converter.process_all_pdfs()
        print("PDF转换完成")
    elif args.question:
        # 创建保险代理并回答问题
        agent = InsuranceAgent(map_file, output_directory)
        agent.agent.to_cli_sync()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()