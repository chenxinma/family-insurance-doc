from pdf_converter import PDFToTxtConverter
import json
import os

def test_sha1_feature():
    # 创建测试目录和文件
    converter = PDFToTxtConverter("./insurance-docs", "./processed-docs", "./processed-docs/map.json")
    
    # 处理所有PDF文件
    converter.process_all_pdfs()
    
    # 检查map.json是否包含sha1_hash字段
    with open("./processed-docs/map.json", 'r', encoding='utf-8') as f:
        file_map = json.load(f)
    
    print("Checking SHA1 hash in map.json entries...")
    for title, entry in file_map.items():
        if "sha1_hash" in entry:
            print(f"✓ {title} has SHA1 hash: {entry['sha1_hash'][:20]}...")
        else:
            print(f"✗ {title} is missing SHA1 hash")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_sha1_feature()