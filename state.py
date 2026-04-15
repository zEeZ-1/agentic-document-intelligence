from langchain.agents import AgentState
from typing import List



class State(AgentState):
    file_path: str = ""
    chunks: List[dict] = []
    result: str = ""
    format_txt: str = ""