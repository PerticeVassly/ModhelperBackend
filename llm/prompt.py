from abc import ABC, abstractmethod
from typing import List
import logging
import textwrap
from model import *
import json

logger = logging.getLogger("prompt")

class Prompt(ABC):
    """
    Basic class for all prompts.

    Contaings a template and method of how to render it.
    """
    def __init__(self, template: str):
        self.template = template

    @abstractmethod
    def render(self, kwargs : list[str]) -> str:
        pass

class ExtractorPrompt(Prompt):

    def __init__(self):
        template = textwrap.dedent("""
            针对给定的文本，回答以下问题并且提取关键信息
            1. 问题是否是Minecraft/我的世界/MC 模组相关问题，使用0/1表示
            2. 如果是Minecraft/我的世界/MC 模组相关问题，提取出问题中的感兴趣实体信息，包括模组名称、物品名称、方块名称，世界名称群系名称，使用json格式返回结果；若不是MCmod相关问题则反回空列表即可
            3. 如果是MC相关问题，判断问题的意图，从“模组基本信息查询”，“模组玩法攻略查询”，“模组推荐”，“整合包定制”，四个意图中选择一个返回，分别使用 basic_info、gameplay_guide、mod_recommendation、pack_customization表示；如果不是MCmod相关问题，返回空字符串即可
            返回格式如下, 请严格遵守：                       
            {response_format}
            文本: {input_text}
        """)
        super().__init__(template)

    def render(self, input_text : str) -> str:
        ans = self.template.format(
            input_text=input_text,
            response_format=json.dumps(ExtractedInfo.model_json_schema(), ensure_ascii=False, indent=2)
        )
        return ans

class RetryPrompt(Prompt):
    def __init__(self):
        template = textwrap.dedent("""
            你的回答格式不正确，请严格按照以下格式返回结果：
            {response_format}
        """)
        super().__init__(template)

    def render(self, response_format : BaseModel) -> str:
        return self.template.format(
            response_format=json.dumps(response_format.model_json_schema(), ensure_ascii=False, indent=2)
        )
      
class RAGPrompt(Prompt):
    def __init__(self):
        template = textwrap.dedent("""
            我将给你一些相关参考资料作为背景知识参考，请你根据这些信息回答问题，但是你不能直接引用这些信息，也不能在回答中透露出你是从这些信息中获取的答案。
            参考资料：{context}
            问题：{question}
        """)
        super().__init__(template)

    def render(self, context_content: Reference, question: str) -> str:
        ans = self.template.format(
            context= json.dumps(context_content, ensure_ascii=False),
            question=question
        )
        return ans

class NonRAGPrompt(Prompt):
    def __init__(self):
        template = textwrap.dedent("""
            {question}
        """)
        super().__init__(template)

    def render(self, question) -> str:
        ans = self.template.format(
            question=question
        )
        return ans
    
class SummarizePrompt(Prompt):
    def __init__(self):
        template = textwrap.dedent("""
            你是一名对话助手，擅长为对话内容生成简短的概括性标题。
            请根据以下对话内容，评估原始标题是否仍能概括此段对话。若能，请返回原始标题；若不能，请生成一个新的标题。
            请严格使用JSON格式返回结果，不要有额外输出，格式如下例：
            {response_format}
            原始标题：{old_name}
            对话内容：{conversation_messages}
        """)
        super().__init__(template)

    def render(self, messages: List[MessageInfo], old_name : str) -> str:
        ans = self.template.format(
            old_name=old_name,
            conversation_messages="\n".join(f"user: {m.user_message}\nassistant: {m.assistant_message}" for m in messages),
            response_format=json.dumps(SummarizeTitle.model_json_schema(), ensure_ascii=False, indent=2)
        )
        return ans
