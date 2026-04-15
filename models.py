from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.embeddings import DashScopeEmbeddings
import os

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
SEED_API_KEY = os.getenv("SEED_API_KEY")


qwen_max = ChatOpenAI(
    model_name="qwen3-max",
    api_key = DASHSCOPE_API_KEY ,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1" ,
    # extra_body={"enable_thinking": True}

)
qwen_turbo = ChatOpenAI(
    model_name="qwen-turbo",
    api_key = DASHSCOPE_API_KEY ,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

qwen35_plus = ChatOpenAI(
    model_name="qwen3.5-plus",
    api_key = DASHSCOPE_API_KEY ,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
      # 禁用思考模式以避免 tool_choice 错误
    # extra_body={"enable_thinking": False}
)

Seed2_pro = ChatOpenAI(
    model_name="doubao-seed-2-0-pro-260215",
    api_key = SEED_API_KEY ,
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)

Seed2_mini = ChatOpenAI(
    model_name="doubao-seed-2-0-mini-260215",
    api_key = SEED_API_KEY ,
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)

doubao_embedding = OpenAIEmbeddings(
    model="doubao-embedding-text-240715",
    api_key = SEED_API_KEY ,
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)

qwen_embedding_v3 = DashScopeEmbeddings(
    model="text-embedding-v3",
)

qwen3_vl = ChatOpenAI(
    model_name="qwen3-vl-plus",
    api_key = DASHSCOPE_API_KEY ,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)