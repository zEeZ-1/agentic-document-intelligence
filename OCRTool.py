import base64
import io
import cv2
import numpy as np
from PIL import Image
import easyocr
from typing import Union, List, Dict
from langchain.tools import tool , ToolRuntime

class Base64OCR:
    def __init__(self, languages=['ch_sim', 'en']):
        self.languages = languages
        self.reader = None
    
    def _get_reader(self):
        if self.reader is None:
            self.reader = easyocr.Reader(self.languages, gpu=False)
        return self.reader
    
    def base64_to_image(self, base64_string: str) -> np.ndarray:
        """将Base64字符串转换为numpy数组"""
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        return np.array(image)
    
    def extract_text(self, image_input: Union[str, np.ndarray], 
                    preprocess: bool = False, 
                    bbox: List[int] = None) -> List[Dict]:
        """
        从图片或Base64字符串中提取文本
        
        参数:
            image_input: 图片路径、Base64字符串或numpy数组
            preprocess: 是否进行预处理
            bbox: 要识别的区域坐标 [x1, y1, x2, y2]（相对坐标，0-1000）
            
        返回:
            包含文本、置信度和坐标的字典列表
        """
        reader = self._get_reader()
        
        if isinstance(image_input, str):
            if self._is_base64(image_input):
                image = self.base64_to_image(image_input)
            else:
                image = cv2.imread(image_input)
                if image is not None:
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image = image_input
        
        if bbox:
            img_height, img_width = image.shape[:2]
            x1 = int(bbox[0] / 1000 * img_width)
            y1 = int(bbox[1] / 1000 * img_height)
            x2 = int(bbox[2] / 1000 * img_width)
            y2 = int(bbox[3] / 1000 * img_height)
            
            x1 = max(0, min(x1, img_width))
            y1 = max(0, min(y1, img_height))
            x2 = max(0, min(x2, img_width))
            y2 = max(0, min(y2, img_height))
            
            if x2 <= x1 or y2 <= y1:
                return []
            
            image = image[y1:y2, x1:x2]
        
        if preprocess:
            image = self._preprocess_image(image)
        
        result = reader.readtext(image)
        return self._format_result(result)
    
    def _is_base64(self, s: str) -> bool:
        """检查字符串是否为Base64编码"""
        try:
            if s.startswith('data:image'):
                return True
            base64.b64decode(s)
            return True
        except:
            return False
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """图像预处理"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary
    
    def _format_result(self, result) -> List[Dict]:
        """格式化OCR结果"""
        formatted = []
        if result:
            for bbox, text, confidence in result:
                text_info = {
                    'text': text,
                    'confidence': float(confidence),
                    'bbox': [[int(point[0]), int(point[1])] for point in bbox]
                }
                formatted.append(text_info)
        return formatted

# 创建全局OCR实例
ocr_helper = Base64OCR(languages=['ch_sim', 'en'])

@tool
def ocr_extract_text(runtime : ToolRuntime, preprocess: bool = False, bbox: List[int] = None) -> str:
    """
    从Base64编码的图片或图片路径中提取文本,当你看不清某处图片内容时使用。最好一次只识别一小块区域。
    
    参数:
        preprocess (bool): 是否对图片进行预处理，默认为False
        bbox (List[int]): 要识别的区域坐标 [x1, y1, x2, y2]（相对坐标，0-1000）, 必须填入，不能为空。
        
    返回:
        str: 提取的文本内容，每行文本包含文本内容和置信度
    """
    if(bbox == None): 
        return "未指定识别区域"
    
    image_input = runtime.context.image_url
    try:
        results = ocr_helper.extract_text(image_input, preprocess, bbox)
        
        if not results:
            return "未检测到文本内容"
        
        output_lines = []
        for i, item in enumerate(results, 1):
            text = item['text']
            confidence = item['confidence']
            output_lines.append(f"{i}. {text} (置信度: {confidence:.2f})")
        
        return "\n".join(output_lines)
    
    except Exception as e:
        return f"OCR识别失败: {str(e)}"

@tool
def ocr_extract_detailed(image_input: str, preprocess: bool = False) -> str:
    """
    从Base64编码的图片中提取详细文本信息，包含坐标
    
    参数:
        image_input (str): Base64编码的图片字符串或图片文件路径
        preprocess (bool): 是否对图片进行预处理，默认为False
        
    返回:
        str: 详细的文本信息，包含文本、置信度和坐标位置
    """
    try:
        results = ocr_helper.extract_text(image_input, preprocess)
        
        if not results:
            return "未检测到文本内容"
        
        output_lines = []
        for i, item in enumerate(results, 1):
            text = item['text']
            confidence = item['confidence']
            bbox = item['bbox']
            
            output_lines.append(f"文本块 {i}:")
            output_lines.append(f"  内容: {text}")
            output_lines.append(f"  置信度: {confidence:.2f}")
            output_lines.append(f"  坐标: {bbox}")
            output_lines.append("")
        
        return "\n".join(output_lines)
    
    except Exception as e:
        return f"OCR识别失败: {str(e)}"

@tool
def ocr_batch_extract(image_inputs: List[str], preprocess: bool = False) -> str:
    """
    批量从多个Base64编码的图片中提取文本
    
    参数:
        image_inputs (List[str]): Base64编码的图片字符串列表或图片路径列表
        preprocess (bool): 是否对图片进行预处理，默认为False
        
    返回:
        str: 所有图片的提取结果
    """
    try:
        all_results = []
        
        for i, image_input in enumerate(image_inputs, 1):
            results = ocr_helper.extract_text(image_input, preprocess)
            
            if results:
                text_content = "\n".join([item['text'] for item in results])
                all_results.append(f"图片 {i}:\n{text_content}\n")
            else:
                all_results.append(f"图片 {i}: 未检测到文本内容\n")
        
        return "\n".join(all_results)
    
    except Exception as e:
        return f"批量OCR识别失败: {str(e)}"

if __name__ == "__main__":
    # 测试Base64 OCR
    test_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    result = ocr_extract_text.invoke(test_base64)
    print(result)
