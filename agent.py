from state import State
from langchain.agents import create_agent , AgentState
from deepagents import create_deep_agent , CompiledSubAgent
from models import qwen_max , qwen_turbo , qwen35_plus , Seed2_pro , Seed2_mini , doubao_embedding , qwen_embedding_v3 , qwen3_vl
from langgraph.graph import StateGraph , END , START
from pydantic import BaseModel
from langchain.tools import tool
from pydantic import BaseModel , Field
from typing import List
from pdf_parse import parse_pdf_to_image_blocks
from OCRTool import ocr_extract_text


import os
from dotenv import load_dotenv
from langsmith import traceable

load_dotenv()

@traceable

def shunt(state: State) :
    path = state.get("file_path")

    if(path.endswith(".docx")):
        return "docx"
    if(path.endswith(".pdf")):
        return "pdf"
    if(path.endswith(".txt")):
        return "txt"

@traceable

def docx_parse(state: State):
    path = state.get("file_path")
    from docx_parse import parse_docx_to_structured_list
    chunks = parse_docx_to_structured_list(path, use_base64=True)
    return {"chunks":chunks}

@traceable

def pdf_parse(state: State):
    path = state.get("file_path")
    chunks = parse_pdf_to_image_blocks(path, model=qwen35_plus)
    return {"chunks":chunks}

@traceable

def txt_parse(state: State):
    pass


@tool 
def image_subagent(image_url: str , description: str = ""):
    """
    专门用于理解图片chunks ,
    参数:
        image_url (str): 图片的base64编码字符串或地址
        description (str): 图片的simple_description
    """

    class Context(BaseModel):
        image_url: str = Field(description="图片的base64编码字符串或地址")
        description: str = Field(description="图片的simple_description")


    image_agent = create_agent(
        model=qwen3_vl,
        system_prompt="你是一个图片理解助手，是理解图片的专家,你需要描述图片的内容，内容覆盖全面，但也要简短，不要进行额外的推理拓展，对于文字元素，直接复述文字内容，不需要额外解释，对于表格元素，用文字输出表格，不需要额外解释，对于其它元素，进行简短的描述。对于难以看清的文字，参考OCR结果",
        tools = [ocr_extract_text] , 
        context_schema = Context
    )

    result = image_agent.invoke({
        "messages" : [
            {"role":"user","content":[
                {"type":"image_url","image_url":{"url":f"{image_url}"}} ,
                {"type":"text","text":f"图片的simple_description为：{description}.\n "}
            ]}
        ]
    } ,
    context=Context(image_url=image_url, description=description))
    return result["messages"][-1].content

@tool
def text_subagent(text: str):
    """
    专门用于理解文本chunks ,
    参数:
        text (str): 文本内容
    """
    return text 
    text_agent = create_agent(
        model=qwen35_plus,
        system_prompt="你是一个文本理解助手，是理解文本的专家,你需要描述文本的内容，尽可能详细",
    )
    result = text_agent.invoke({
        "messages" : [
            {"role":"user","content":[
                {"type":"text","text":f"{text}"}
            ]}
        ]})
    return result["messages"][-1].content

@tool
def table_subagent(table: str):
    """
    专门用于理解表格chunks ,
    参数:
        table (str): 表格内容
    """
    return table
    table_agent = create_agent(
        model=qwen35_plus,
        system_prompt="你是一个表格理解助手，是理解表格的专家,你需要描述表格的内容，尽可能详细",
    )
    result = table_agent.invoke({
        "messages" : [
            {"role":"user","content":[
                {"type":"text","text":f"{table}"}
            ]}
        ]})
    return result["messages"][-1].content


@traceable



def solve_chunks(state: State):
    chunks = state.get("chunks" , [])
    

    # class custom_state(AgentState):
    #     chunks: list = []

    # agent = create_agent(
    #     model=qwen35_plus,
    #     tools=[image_subagent , text_subagent , table_subagent],
    #     system_prompt="你是一个智能助手，是一个专业的文档理解助手，你可以理解图片、文本和表格等不同类型的文档内容。\n你会得到一个文档分割后的chunks，你需要选择合适的方式理解每个chunk，并且同时还要整体理解整个文档的内容。",
    #     state_schema=custom_state,
    # )
    
    # result = agent.invoke({
    #     "messages" : [{"role":"user","content":"请理解这个文档"}] ,
    #     "chunks":chunks
    #     } 
    # )
    res = ""
    for i, chunk in enumerate(chunks):
        chunk_type = chunk.get("type", "unknown")
        content = chunk.get("content", "")
        description = chunk.get("description", "")
        
        if chunk_type == "text":
            if content.startswith("data:image"):
                res += f"\n[文本 {i+1}] \n" + description + "\n" + image_subagent.invoke({"image_url": content , "description": description}) + "\n"
            else:
                res += f"\n[文本 {i+1}] \n" + description + "\n" + text_subagent.invoke({"text": content}) + "\n"
        elif chunk_type == "table":
            if content.startswith("data:image"):
                res += f"\n[表格 {i+1}] \n" + description + "\n" + image_subagent.invoke({"image_url": content , "description":description}) + "\n"
            else:
                res += f"\n[表格 {i+1}] \n" + description + "\n" + table_subagent.invoke({"table": content}) + "\n"
        elif chunk_type == "image":
            res += f"\n[图片 {i+1}] \n" + description + "\n" + image_subagent.invoke({"image_url": content , "description":description}) + "\n"
        else:
            res += f"\n[未知类型 {i+1}] \n" + description + "\n" + str(chunk) + "\n" + image_subagent.invoke({"image_url": content , "description":description}) + "\n"

    return {"result":res}


def format_txt(state: State):
    result = state.get("result" , "")
    Format_agent = create_agent(
        model=qwen35_plus,
        system_prompt="你是一个文本格式化助手，是格式化文本的专家。你会收到一篇多模态文档分割处理后的多块文本内容描述。你需要将这些块合成，以标准的文档格式合并为一篇完整的文档。",
    )
    res = Format_agent.invoke({
        "messages" : [
            {"role":"user","content":f"各块内容如下：\n{result}\n请将这些块合成，以标准的文档格式合并为一篇完整的文档。"}
        ]})
    return {"format_txt":res["messages"][-1].content}

    

graph = StateGraph(State)

graph.add_node("docx_parse" , docx_parse)
graph.add_node("pdf_parse" , pdf_parse)
graph.add_node("txt_parse" , txt_parse)
graph.add_node("solve_chunks" , solve_chunks)
graph.add_node("format_txt" , format_txt)


graph.add_conditional_edges(
    START , 
    shunt , 
    {
        "docx":"docx_parse" , 
        "pdf":"pdf_parse" , 
        "txt":"txt_parse"
    }

)

graph.add_edge("docx_parse" , "solve_chunks")
graph.add_edge("pdf_parse" , "solve_chunks")
graph.add_edge("txt_parse" , "solve_chunks")
graph.add_edge("solve_chunks" , "format_txt")
graph.add_edge("format_txt" , END)


ADI = graph.compile()

if __name__ == "__main__":
    response = ADI.invoke({
        "file_path":"/home/zrz/ADI/note'.pdf"
    })

    with open("note.md" , "w") as f:
        f.write(response["format_txt"])
        
