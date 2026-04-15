from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph
import os
import base64
import struct

def get_image_mime_type(image_data):
    """根据图片数据的魔数检测MIME类型"""
    if image_data.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'image/png'
    elif image_data.startswith(b'\xff\xd8'):
        return 'image/jpeg'
    elif image_data.startswith(b'GIF87a') or image_data.startswith(b'GIF89a'):
        return 'image/gif'
    elif image_data.startswith(b'BM'):
        return 'image/bmp'
    elif image_data.startswith(b'II\x2a\x00') or image_data.startswith(b'MM\x00\x2a'):
        return 'image/tiff'
    else:
        return 'image/png'

def iter_block_items(parent):
    if hasattr(parent, 'element') and hasattr(parent.element, 'body'):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise ValueError("something's not right")

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)

def has_image(para):
    for run in para.runs:
        if run._element.xpath('.//pic:pic'):
            return True
    return False

def extract_images_from_doc(doc, output_dir="extracted_images", use_base64=False):
    os.makedirs(output_dir, exist_ok=True)
    image_map = {}
    image_count = 0
    
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            image_count += 1
            image_data = rel.target_part.blob
            mime_type = get_image_mime_type(image_data)
            extension = mime_type.split('/')[1]
            image_filename = os.path.join(output_dir, f"image_{image_count}.{extension}")
            
            if use_base64:
                image_map[rel.rId] = {
                    "path": image_filename,
                    "base64": base64.b64encode(image_data).decode('utf-8'),
                    "mime_type": mime_type
                }
            else:
                with open(image_filename, "wb") as f:
                    f.write(image_data)
                image_map[rel.rId] = image_filename
    
    return image_map, image_count

def parse_docx_to_structured_list(docx_path, output_dir="extracted_images", use_base64=False, vl_format=False):
    result = []
    doc = Document(docx_path)
    image_map, total_images = extract_images_from_doc(doc, output_dir, use_base64)
    image_index = 0
    
    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            if has_image(block):
                image_index += 1
                image_key = list(image_map.keys())[image_index - 1]
                image_info = image_map[image_key]
                
                if use_base64:
                    result.append({
                        "type": "image",
                        "content": f"data:{image_info['mime_type']};base64,{image_info['base64']}",
                        "description": block.text.strip() if block.text else ""
                    })
                else:
                    result.append({
                        "type": "image",
                        "content": image_info,
                        "description": block.text.strip() if block.text else ""
                    })
            elif block.text.strip():
                result.append({
                    "type": "text",
                    "content": block.text.strip(),
                    "description": ""
                })
        elif isinstance(block, Table):
            table_data = []
            for row in block.rows:
                row_data = [cell.text.strip() for cell in row.cells]
                table_data.append(row_data)
            table_str = "\n".join([" | ".join(row) for row in table_data])
            result.append({
                "type": "table",
                "content": table_str,
                "description": f"表格({len(block.rows)}行×{len(block.columns)}列)"
            })
    
    return result

if __name__ == "__main__":
    result = parse_docx_to_structured_list("example.docx", use_base64=True)
    print(result)
    print("=== 结构化内容 ===")
    for i, item in enumerate(result, 1):
        if item["type"] == "text":
            print(f"[{i}] 📝 文本")
            print(f"    内容: {item['content']}")
        elif item["type"] == "image":
            print(f"[{i}] 📷 图片")
            print(f"    路径: {item['content']}")
            with open('image.png', 'wb') as f:
                f.write(base64.b64decode(item['content']))
            if item.get('text'):
                print(f"    说明: {item['text']}")
        elif item["type"] == "table":
            print(f"[{i}] 📊 表格 ({item['rows']} 行 × {item['columns']} 列)")
            for row in item['content'][:3]:
                print(f"    {row}")
            if len(item['content']) > 3:
                print(f"    ... (还有 {len(item['content'])-3} 行)")
        print()
    
    print("=== 统计信息 ===")
    text_count = sum(1 for item in result if item["type"] == "text")
    image_count = sum(1 for item in result if item["type"] == "image")
    table_count = sum(1 for item in result if item["type"] == "table")
    print(f"总块数: {len(result)}")
    print(f"文本数: {text_count}")
    print(f"图片数: {image_count}")
    print(f"表格数: {table_count}")