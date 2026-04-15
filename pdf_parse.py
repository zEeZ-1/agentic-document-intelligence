import fitz
import os
import base64
import io
import json
from PIL import Image
import numpy as np
from langchain_core.messages import HumanMessage, SystemMessage

def pdf_page_to_image(page, zoom=2):
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img_bytes = pix.tobytes("png")
    return Image.open(io.BytesIO(img_bytes))

def detect_content_blocks_with_vlm(image, model):
    prompt = """请分析这张图片，将其分成不同的内容块。你需要返回每个块的边界框坐标和类型。
            块的分割规则：
            1.不用细致分析图片，只用大致看一下图片要分成几部分。
            2.一块区域都是文本，即可看作一块。
            3.一张图片或表格也可作为一块。
            4.如果一张图片必须和文字搭配才有意义的话，则和这些文字划分在同一块。
            5.根据你的理解一大块区域如果是进行列举一些相同性质的元素，则这一区域可以划分为一块。
            6.分割的块数尽可能少。
            7.可以一整张图片只作为一个块。
            8.分割时为了防止因误差而导致内容缺失，可以适当增大边界。
请按以下JSON格式返回，只返回JSON，不要其他内容：
{
    "blocks": [
        {
            "type": "text|table|image|heading|list",
            "bbox": [x1, y1, x2, y2],
            "description": "简要描述这个块的内容"
        }
    ]
}

坐标说明：
- x1, y1: 左上角坐标（0-1000）
- x2, y2: 右下角坐标（0-1000）
- 坐标范围：0-1000（相对坐标）

必须强制扩大边界范围10/1000！！！


"""
    
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    message = HumanMessage(
        content=[
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}},
            {"type": "text", "text": prompt}
        ]
    )
    
    response = model.invoke([message])
    
    try:
        content = response.content if hasattr(response, 'content') else str(response)
        json_match = content.find('{')
        if json_match != -1:
            json_str = content[json_match:]
            last_brace = json_str.rfind('}')
            if last_brace != -1:
                json_str = json_str[:last_brace+1]
            result = json.loads(json_str)
            return result.get("blocks", [])
    except Exception as e:
        print(f"解析VLM响应失败: {e}")
    
    return []

def crop_image_blocks(image, blocks):
    cropped_blocks = []
    
    img_width, img_height = image.size
    
    for block in blocks:
        try:
            bbox = block["bbox"]
            x1 = int(bbox[0] / 1000 * img_width)
            y1 = int(bbox[1] / 1000 * img_height)
            x2 = int(bbox[2] / 1000 * img_width)
            y2 = int(bbox[3] / 1000 * img_height)
            
            x1 = max(0, min(x1, img_width))
            y1 = max(0, min(y1, img_height))
            x2 = max(0, min(x2, img_width))
            y2 = max(0, min(y2, img_height))
            
            if x2 <= x1 or y2 <= y1:
                continue
            
            cropped = image.crop((x1, y1, x2, y2))
            
            buffered = io.BytesIO()
            cropped.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            block_type = block["type"]
            description = block.get("description", "")
            
            if block_type in ["text", "heading", "list"]:
                cropped_blocks.append({
                    "type": "text",
                    "content": f"data:image/png;base64,{img_base64}",
                    "description": description
                })
            elif block_type == "table":
                cropped_blocks.append({
                    "type": "table",
                    "content": f"data:image/png;base64,{img_base64}",
                    "description": description
                })
            elif block_type == "image":
                cropped_blocks.append({
                    "type": "image",
                    "content": f"data:image/png;base64,{img_base64}",
                    "description": description
                })
        except Exception as e:
            print(f"裁剪块失败: {e}")
            continue
    
    return cropped_blocks

def parse_pdf_to_image_blocks(pdf_path, model, output_dir="extracted_blocks", zoom=2):
    os.makedirs(output_dir, exist_ok=True)
    result = []
    
    doc = fitz.open(pdf_path)
    
    for page_num, page in enumerate(doc):
        print(f"正在处理第 {page_num + 1} 页...")
        image = pdf_page_to_image(page, zoom)
        
        blocks = detect_content_blocks_with_vlm(image, model)
        
        if not blocks:
            print(f"  第 {page_num + 1} 页未检测到内容块，使用整页")
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            result.append({
                "type": "text",
                "content": f"data:image/png;base64,{img_base64}",
                "description": f"第{page_num + 1}页"
            })
        else:
            print(f"  第 {page_num + 1} 页检测到 {len(blocks)} 个内容块")
            cropped_blocks = crop_image_blocks(image, blocks)
            
            for block in cropped_blocks:
                block["page"] = page_num + 1
                result.append(block)
    
    doc.close()
    return result

def parse_pdf_simple_images(pdf_path, output_dir="extracted_pages", zoom=2, use_base64=True):
    os.makedirs(output_dir, exist_ok=True)
    result = []
    
    doc = fitz.open(pdf_path)
    
    for page_num, page in enumerate(doc):
        image = pdf_page_to_image(page, zoom)
        
        if use_base64:
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            result.append({
                "type": "page",
                "content": img_base64,
                "mime_type": "image/png",
                "image": f"data:image/png;base64,{img_base64}",
                "page": page_num + 1
            })
        else:
            image_path = os.path.join(output_dir, f"page_{page_num + 1}.png")
            image.save(image_path)
            
            result.append({
                "type": "page",
                "content": image_path,
                "page": page_num + 1
            })
    
    doc.close()
    return result

if __name__ == "__main__":
    from models import qwen3_vl
    
    result = parse_pdf_simple_images("example.pdf", use_base64=True)
    
    print("=== PDF页面图片 ===")
    for i, item in enumerate(result, 1):
        print(f"[{i}] � 第{item['page']}页")
        print(f"    类型: {item['type']}")
        if item.get('mime_type'):
            print(f"    MIME: {item['mime_type']}")
        print()
    
    print("=== 统计信息 ===")
    print(f"总页数: {len(result)}")