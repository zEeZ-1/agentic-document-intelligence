# Agentic Document Intelligence (ADI)

一个基于代理的智能文档处理系统，能够解析和理解多种类型的文档，包括PDF、DOCX和TXT文件。

## 功能特点

- **多格式文档支持**：支持PDF、DOCX和TXT文件的解析
- **多模态处理**：能够处理文档中的文本、表格和图片内容
- **智能分块**：自动将文档分割成有意义的chunks
- **专业子代理**：为不同类型的内容（文本、表格、图片）提供专门的处理代理
- **结构化输出**：将处理后的内容格式化为标准文档格式

## 技术架构

- **核心框架**：LangGraph
- **模型**：Qwen系列模型（qwen35_plus, qwen3_vl等）
- **文档解析**：
  - PDF解析：使用自定义的`pdf_parse.py`
  - DOCX解析：使用自定义的`docx_parse.py`
  - OCR功能：使用`OCRTool.py`进行文本提取

## 目录结构

```
ADI/
├── agent.py          # 主代理逻辑
├── OCRTool.py        # OCR工具
├── pdf_parse.py      # PDF解析模块
├── docx_parse.py     # DOCX解析模块
├── GLM_OCR.py        # GLM OCR相关功能
├── GLM_file_parse.py # GLM文件解析相关功能
├── models.py         # 模型配置
├── state.py          # 状态管理
├── note.md           # 示例输出
├── .gitignore        # Git忽略文件
├── README.md         # 项目说明
└── LICENSE           # 许可证
```

## 安装方法

1. 克隆项目
   ```bash
   git clone https://github.com/zEeZ-1/agentic-document-intelligence.git
   cd agentic-document-intelligence
   ```

2. 安装依赖
   ```bash
   pip install langchain langgraph deepagents pydantic python-dotenv langsmith
   ```

3. 配置环境变量
   创建`.env`文件并添加必要的API密钥：
   ```
   # 模型API密钥
   QWEN_API_KEY=your_qwen_api_key
   ```

## 使用示例

### 基本使用

```python
from agent import ADI

# 处理PDF文件
response = ADI.invoke({
    "file_path": "path/to/your/document.pdf"
})

# 获取格式化后的结果
formatted_output = response["format_txt"]
print(formatted_output)

# 保存结果到文件
with open("output.md", "w") as f:
    f.write(formatted_output)
```

### 处理不同类型的文档

```python
# 处理DOCX文件
response = ADI.invoke({
    "file_path": "path/to/your/document.docx"
})

# 处理TXT文件
response = ADI.invoke({
    "file_path": "path/to/your/document.txt"
})
```

## 工作流程

1. **文档类型识别**：根据文件扩展名识别文档类型
2. **文档解析**：使用相应的解析器将文档分割成chunks
3. **内容处理**：
   - 对于文本chunks：使用文本子代理处理
   - 对于表格chunks：使用表格子代理处理
   - 对于图片chunks：使用图片子代理处理（包含OCR）
4. **内容整合**：将处理后的chunks整合成标准文档格式

## 模型配置

项目使用了多个Qwen系列模型，配置在`models.py`文件中。您可以根据需要修改模型配置以获得最佳性能。

## 注意事项

- 处理大型文档可能需要较长时间
- 某些复杂表格可能需要额外的处理
- 图片中的文字识别 accuracy 取决于OCR工具的性能

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

本项目使用MIT许可证。详情请见LICENSE文件。

## 联系方式

- GitHub: [zEeZ-1](https://github.com/zEeZ-1)
