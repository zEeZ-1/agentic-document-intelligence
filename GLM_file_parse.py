from zai import ZhipuAiClient
from langchain_community.document_loaders import PyPDFLoader , Docx2txtLoader
import os   

client = ZhipuAiClient(api_key="62806958c52d42cea84dc958b704b124.SmgMa52z5JwnKS9t")
# 用于上传发起文件解析任务
# 返回task_id
# response = client.file_parser.create(file=open('example.pdf', 'rb'), file_type='pdf', tool_type='lite')
# task_id = getattr(response, "task_id", None)

# # 获取文件内容抽取: format_type = text / download_link
# # text模式最长返回1m以内的文本内容，download_link响应更快
# res_response = client.file_parser.content(task_id=task_id, format_type="download_link")

# print(response.json())  # 新版推荐用法
# print(res_response.json())
# print(response.content.decode('utf-8')) # 旧版解码字节流用法依然支持

def file_parser_sync_example():
    """
    示例：提交文件解析任务并等待结果返回。
    """
    # 创建解析任务
    # 请修改为本地文件路径
    file_path = '/home/zrz/ADI/example.docx'
    with open(file_path, 'rb') as f:
        # print(f.read())
        print("正在提交文件解析任务 ...")
        response = client.file_parser.create_sync(
            file=f,
            file_type="docx",
            tool_type="prime-sync",
        )
        print("任务创建成功，响应如下：")
        print(response)

    print("File parser demo completed.")

def langchian_load() : 
    loader = Docx2txtLoader(file_path = '/home/zrz/ADI/example.docx')
    documents = loader.load()
    print(documents)

if __name__ == "__main__":
    print("=== 文件同步解析快速演示（仅限 Prime） ===\n")
    file_parser_sync_example()
    # print("\n=== langchain_load示例 ===\n")
    # langchian_load()