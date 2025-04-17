"""
LLM编辑器模块
用于处理与大语言模型的交互
"""

import Writer.PrintUtils
import Writer.Prompts

import json
from .Prompts import JSON_PARSE_ERROR


def GetFeedbackOnOutline(Interface, _Logger, _Outline: str):

    # Setup Initial Context History
    History = []
    History.append(Interface.BuildSystemQuery(Writer.Prompts.CRITIC_OUTLINE_INTRO))

    StartingPrompt: str = Writer.Prompts.CRITIC_OUTLINE_PROMPT.format(_Outline=_Outline)

    _Logger.Log("Prompting LLM To Critique Outline", 5)
    History.append(Interface.BuildUserQuery(StartingPrompt))
    History = Interface.SafeGenerateText(
        _Logger, History, Writer.Config.REVISION_MODEL, _MinWordCount=70
    )
    _Logger.Log("Finished Getting Outline Feedback", 5)

    return Interface.GetLastMessageText(History)


def GetOutlineRating(
    Interface,
    _Logger,
    _Outline: str,
):

    # Setup Initial Context History
    History = []
    History.append(Interface.BuildSystemQuery(Writer.Prompts.OUTLINE_COMPLETE_INTRO))

    StartingPrompt: str = Writer.Prompts.OUTLINE_COMPLETE_PROMPT.format(
        _Outline=_Outline
    )

    _Logger.Log("Prompting LLM To Get Review JSON", 5)

    History.append(Interface.BuildUserQuery(StartingPrompt))
    History = Interface.SafeGenerateText(
        _Logger, History, Writer.Config.EVAL_MODEL, _Format="json"
    )
    _Logger.Log("Finished Getting Review JSON", 5)

    Iters: int = 0
    while True:

        RawResponse = Interface.GetLastMessageText(History)
        RawResponse = RawResponse.replace("`", "")
        RawResponse = RawResponse.replace("json", "")

        try:
            Iters += 1
            Rating = json.loads(RawResponse)["IsComplete"]
            _Logger.Log(f"Editor Determined IsComplete: {Rating}", 5)
            return Rating
        except Exception as E:
            if Iters > 4:
                _Logger.Log("Critical Error Parsing JSON", 7)
                return False
            _Logger.Log("Error Parsing JSON Written By LLM, Asking For Edits", 7)
            EditPrompt: str = JSON_PARSE_ERROR.format(_Error=str(E))
            History.append(Interface.BuildUserQuery(EditPrompt))
            _Logger.Log("Asking LLM TO Revise", 7)
            History = Interface.SafeGenerateText(
                _Logger, History, Writer.Config.EVAL_MODEL, _Format="json"
            )
            _Logger.Log("Done Asking LLM TO Revise JSON", 6)


def GetFeedbackOnChapter(Interface, _Logger, _Chapter: str, _Outline: str):

    # Setup Initial Context History
    History = []
    History.append(
        Interface.BuildSystemQuery(
            Writer.Prompts.CRITIC_CHAPTER_INTRO.format(_Chapter=_Chapter)
        )
    )

    # Disabled seeing the outline too.
    StartingPrompt: str = Writer.Prompts.CRITIC_CHAPTER_PROMPT.format(
        _Chapter=_Chapter, _Outline=_Outline
    )

    _Logger.Log("Prompting LLM To Critique Chapter", 5)
    History.append(Interface.BuildUserQuery(StartingPrompt))
    Messages = Interface.SafeGenerateText(
        _Logger, History, Writer.Config.REVISION_MODEL
    )
    _Logger.Log("Finished Getting Chapter Feedback", 5)

    return Interface.GetLastMessageText(Messages)


# Switch this to iscomplete true/false (similar to outline)
def GetChapterRating(Interface, _Logger, _Chapter: str):

    # Setup Initial Context History
    History = []
    History.append(Interface.BuildSystemQuery(Writer.Prompts.CHAPTER_COMPLETE_INTRO))

    StartingPrompt: str = Writer.Prompts.CHAPTER_COMPLETE_PROMPT.format(
        _Chapter=_Chapter
    )

    _Logger.Log("Prompting LLM To Get Review JSON", 5)
    History.append(Interface.BuildUserQuery(StartingPrompt))
    History = Interface.SafeGenerateText(
        _Logger, History, Writer.Config.EVAL_MODEL
    )
    _Logger.Log("Finished Getting Review JSON", 5)

    Iters: int = 0
    while True:

        RawResponse = Interface.GetLastMessageText(History)
        RawResponse = RawResponse.replace("`", "")
        RawResponse = RawResponse.replace("json", "")

        try:
            Iters += 1
            Rating = json.loads(RawResponse)["IsComplete"]
            _Logger.Log(f"Editor Determined IsComplete: {Rating}", 5)
            return Rating
        except Exception as E:
            if Iters > 4:
                _Logger.Log("Critical Error Parsing JSON", 7)
                return False

            _Logger.Log("Error Parsing JSON Written By LLM, Asking For Edits", 7)
            EditPrompt: str = JSON_PARSE_ERROR.format(_Error=str(E))
            History.append(Interface.BuildUserQuery(EditPrompt))
            _Logger.Log("Asking LLM TO Revise", 7)
            History = Interface.SafeGenerateText(
                _Logger, History, Writer.Config.EVAL_MODEL
            )
            _Logger.Log("Done Asking LLM TO Revise JSON", 6)


class LLMEditor:
    """
    LLM编辑器类
    管理与LLM的交互和响应处理
    """
    
    def __init__(self, interface, logger):
        """
        初始化LLM编辑器
        
        参数:
            interface: LLM接口实例
            logger: 日志记录器实例
        """
        self.interface = interface
        self.logger = logger
        
    def generate(self, prompt, model="default", format=None):
        """
        生成LLM响应
        
        参数:
            prompt (str): 提示文本
            model (str): 要使用的模型名称
            format (str): 期望的响应格式(如"json")
            
        返回:
            str: LLM的响应文本
        """
        self.logger.log("向LLM发送生成请求", 5)
        messages = [self.interface.build_user_query(prompt)]
        
        response = self.interface.safe_generate(
            self.logger,
            messages,
            model,
            format=format
        )
        
        self.logger.log("已完成LLM响应生成", 5)
        return self.interface.get_last_message_text(response)
        
    def parse_json_response(self, response, max_retries=4):
        """
        解析JSON格式的LLM响应
        
        参数:
            response (str): LLM响应文本
            max_retries (int): 最大重试次数
            
        返回:
            dict: 解析后的JSON数据
        """
        # 清理响应文本
        cleaned = response.replace("`", "").replace("json", "")
        
        for i in range(max_retries):
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError as e:
                if i == max_retries - 1:
                    self.logger.log("JSON解析出现严重错误", 7)
                    return {}
                    
                self.logger.log("LLM生成的JSON解析出错,请求修改", 7)
                edit_prompt = JSON_PARSE_ERROR.format(_Error=str(e))
                cleaned = self.generate(edit_prompt, format="json")
                
        return {}
