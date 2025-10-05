# 家庭保险文档项目 (Family Insurance Doc)

## 项目概述
这是一个归档家庭保险合同并形成知识库的工具Agent。该项目通过将PDF格式的保险合同转换为可搜索的文本格式，并构建智能问答系统，帮助用户快速获取保险文档中的关键信息。对于合同文本的检索采用map+filesystem的形式，提供高效便捷的文档管理和查询体验。

## 功能特点

- **PDF文档转换**：读取PDF格式的保险合同，转换并保存为TXT文本格式
- **文档映射管理**：将所有TXT文件的路径、标题、摘要记录到map.json文件中，方便索引和管理
- **智能问答系统**：基于map.json和相关TXT格式的保险合同文本进行交互式问答
- **高效文本检索**：采用ripgrep工具进行文本搜索，快速定位相关内容

## 项目结构

```
├── .gitignore                    # Git忽略配置文件
├── .python-version               # Python版本配置
├── QWEN.md                       # Qwen模型相关说明
├── README.md                     # 项目说明文档
├── insurance_agent.py            # 保险问答代理实现
├── main.py                       # 主入口文件
├── pdf_converter.py              # PDF转TXT功能实现
├── pyproject.toml                # 项目依赖和配置
├── qwen_models.py                # Qwen模型封装
├── rg.exe                        # ripgrep工具可执行文件
├── tests/                        # 测试文件夹
│   └── test_sha1_feature.py      # SHA1功能测试
└── uv.lock                       # 依赖锁定文件
```

## 技术架构

- **pdfplumber**：用于文本提取，将PDF文件转换为TXT文件
- **pydantic-ai**：构建基于命令行的智能Agent
- **ripgrep**：高性能文本搜索工具，用于在文档中快速定位相关内容
- **Qwen模型**：用于提供智能问答能力

## 开发事项

- 依赖组件使用uv进行管理
- 单元测试采用unittest框架
- pydantic-ai API文档：https://ai.pydantic.dev/agents/
- 保险合同PDF文件存放于`./insurance-docs`目录

## 模块设计

### PDFToTxtConverter类
封装PDF文本提取相关功能，主要包括：
- 从PDF文件中提取文本内容
- 将PDF文件转换为TXT格式
- 计算文件的SHA1哈希值，用于检测重复文件
- 更新map.json文件，记录文档信息
- 批量处理目录中的所有PDF文件

### InsuranceAgent类
实现命令行问答功能，主要包括：
- 加载文档映射文件，建立文档索引
- 使用ripgrep工具在文档中搜索相关内容
- 基于Qwen模型提供智能问答服务
- 采用ReAct（Reasoning + Action）框架处理用户查询

## 使用说明

### 准备工作

1. 确保已安装Python 3.12或更高版本
2. 将需要处理的保险合同PDF文件放入`./insurance-docs`目录
3. 安装项目依赖

```bash
uv sync
```

### 转换PDF文件

执行以下命令将PDF文件转换为TXT格式并生成文档映射：

```bash
uv run main.py --convert
```

转换后的TXT文件将保存在处理目录中，同时会生成map.json文件记录文档信息。

### 智能问答

转换完成后，可以使用以下命令启动问答系统：

```bash
uv run main.py --question
```

系统将启动命令行交互式问答界面，您可以提问关于保险文档的问题，系统会基于文档内容提供答案。

## 测试

项目包含基本的测试用例，用于验证SHA1功能是否正常工作：

```bash
uv run tests/test_sha1_feature.py
```

## 环境配置

使用Qwen模型需要配置API密钥环境变量：

```bash
# Windows环境
set BAILIAN_API_KEY=your_api_key_here

# Linux/Mac环境
export BAILIAN_API_KEY=your_api_key_here
```

## 注意事项

- 首次使用时，请确保`insurance-docs`目录存在并包含需要处理的PDF文件
- 问答系统的准确性取决于文档质量和完整性
- ripgrep工具（rg.exe）已包含在项目中，无需单独安装

## 未来计划

- 优化文档摘要提取算法
- 支持更多文件格式（如DOCX、Excel等）
- 增强问答系统的理解和推理能力
