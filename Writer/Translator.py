"""
翻译器模块
用于处理剧本翻译功能
"""

import Writer.PrintUtils
import Writer.Config
import Writer.Prompts

from .Prompts import TRANSLATE_PROMPT, SCENE_TRANSLATE_PROMPT


def TranslatePrompt(Interface, _Logger, _Prompt: str, _Language: str = "French"):

    Prompt: str = Writer.Prompts.TRANSLATE_PROMPT.format(
        _Prompt=_Prompt, _Language=_Language
    )
    _Logger.Log(f"Prompting LLM To Translate User Prompt", 5)
    Messages = []
    Messages.append(Interface.BuildUserQuery(Prompt))
    Messages = Interface.SafeGenerateText(
        _Logger, Messages, Writer.Config.TRANSLATOR_MODEL, _MinWordCount=50
    )
    _Logger.Log(f"Finished Prompt Translation", 5)

    return Interface.GetLastMessageText(Messages)


def TranslateNovel(
    Interface, _Logger, _Chapters: list, _TotalChapters: int, _Language: str = "French"
):

    EditedChapters = _Chapters

    for i in range(_TotalChapters):

        Prompt: str = Writer.Prompts.CHAPTER_TRANSLATE_PROMPT.format(
            _Chapter=EditedChapters[i], _Language=_Language
        )
        _Logger.Log(f"Prompting LLM To Perform Chapter {i+1} Translation", 5)
        Messages = []
        Messages.append(Interface.BuildUserQuery(Prompt))
        Messages = Interface.SafeGenerateText(
            _Logger, Messages, Writer.Config.TRANSLATOR_MODEL
        )
        _Logger.Log(f"Finished Chapter {i+1} Translation", 5)

        NewChapter = Interface.GetLastMessageText(Messages)
        EditedChapters[i] = NewChapter
        ChapterWordCount = Writer.Statistics.GetWordCount(NewChapter)
        _Logger.Log(f"Translation Chapter Word Count: {ChapterWordCount}", 3)

    return EditedChapters


class Translator:
    """
    翻译器类
    处理文本的翻译工作
    """
    
    def __init__(self, llm_editor):
        """
        初始化翻译器
        
        参数:
            llm_editor: LLM编辑器实例
        """
        self.llm = llm_editor
        
    def translate_to_english(self, text, source_lang):
        """
        将文本翻译成英语
        
        参数:
            text (str): 要翻译的文本
            source_lang (str): 源语言
            
        返回:
            str: 翻译后的英文文本
        """
        prompt = TRANSLATE_PROMPT.format(_Prompt=text, _Language=source_lang)
        return self.llm.generate(prompt)
        
    def translate_scene(self, scene, target_lang):
        """
        翻译一个场景到目标语言
        
        参数:
            scene (str): 要翻译的场景内容
            target_lang (str): 目标语言
            
        返回:
            str: 翻译后的场景
        """
        prompt = SCENE_TRANSLATE_PROMPT.format(_Scene=scene, _Language=target_lang)
        return self.llm.generate(prompt)
