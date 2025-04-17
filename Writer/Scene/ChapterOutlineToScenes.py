"""
章节大纲转场景模块
用于将章节大纲转换为场景列表
"""

import Writer.LLMEditor
import Writer.PrintUtils
import Writer.Config
import Writer.Chapter.ChapterGenSummaryCheck
import Writer.Prompts

from ..Prompts import CHAPTER_TO_SCENES

class OutlineToScenesConverter:
    """
    大纲场景转换器类
    用于将章节大纲转换为详细的场景描述
    """
    
    def __init__(self, llm_editor, logger):
        """
        初始化转换器
        
        参数:
            llm_editor: LLM编辑器实例
            logger: 日志记录器实例
        """
        self.llm = llm_editor
        self.logger = logger
        
    def convert_to_scenes(self, chapter_outline, story_outline, base_context=""):
        """
        将章节大纲转换为场景列表
        
        参数:
            chapter_outline (str): 章节大纲
            story_outline (str): 故事大纲
            base_context (str): 基础上下文信息
            
        返回:
            str: 场景列表描述
        """
        self.logger.log("开始将章节大纲转换为场景", 4)
        
        prompt = CHAPTER_TO_SCENES.format(
            _Outline=story_outline,
            _ThisChapter=chapter_outline,
            _BaseContext=base_context
        )
        
        scenes = self.llm.generate(prompt)
        
        self.logger.log("章节大纲转换为场景完成", 4)
        return scenes

def ChapterOutlineToScenes(Interface, _Logger, _ThisChapter:str, _Outline:str, _BaseContext: str = ""):

    # We're now going to convert the chapter outline into a more detailed outline for each scene.
    # The scene by scene outline will be returned, JSONified, and then later converted into fully written scenes
    # These will then be concatenated into chapters and revised


    _Logger.Log(f"Splitting Chapter Into Scenes", 2)
    MesssageHistory: list = []
    MesssageHistory.append(Interface.BuildSystemQuery(Writer.Prompts.DEFAULT_SYSTEM_PROMPT))
    MesssageHistory.append(Interface.BuildUserQuery(Writer.Prompts.CHAPTER_TO_SCENES.format(_ThisChapter=_ThisChapter, _Outline=_Outline)))

    Response = Interface.SafeGenerateText(_Logger, MesssageHistory, Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL, _MinWordCount=100)
    _Logger.Log(f"Finished Splitting Chapter Into Scenes", 5)

    return Interface.GetLastMessageText(Response)
