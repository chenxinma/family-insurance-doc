# 家庭保险文档[family-insurance-doc]

这是一个归档家里买的保险合同并形成知识库的工具Agent。
对于合同文本的检索使用map+filesystem的形式。

## 功能
+ 读取pdf的合同文本，转存为txt
+ 将所有txt文件路径、标题、摘要记录到map.json文件里
+ 基于map.json 和 相关txt的保险合同文本进行问答
+ 问答读取txt文件时采用ripgrep工具搜索相关内容

## 技术架构
+ pdfplumber 文本提取，PDF文件转换为TXT文件
+ pydantic-ai 构建基于cli的Agent

## 开发事项
+ 依赖组件使用uv进行管理
+ 单元测试采用unittest
+ pydantic-ai api文档：https://ai.pydantic.dev/agents/
+ ./insurance-docs 存放了保险合同pdf

## 模块设计
PDFToTxtConverter类封装pdf文本提取相关功能
建立InsuranceAgent类实现命令行问答
