"""
场景大纲转场景模块
用于将场景大纲转换为完整场景内容
"""

import Writer.LLMEditor
import Writer.PrintUtils
import Writer.Config
import Writer.Chapter.ChapterGenSummaryCheck
import Writer.Prompts

from ..Prompts import SCENE_OUTLINE_TO_SCENE

class SceneGenerator:
    """
    场景生成器类
    用于将场景大纲转换为完整的场景内容
    """
    
    def __init__(self, llm_editor, logger):
        """
        初始化场景生成器
        
        参数:
            llm_editor: LLM编辑器实例
            logger: 日志记录器实例
        """
        self.llm = llm_editor
        self.logger = logger
        
    def generate_scene(self, scene_outline, story_outline, base_context=""):
        """
        从场景大纲生成完整场景
        
        参数:
            scene_outline (str): 场景大纲
            story_outline (str): 故事大纲
            base_context (str): 基础上下文信息
            
        返回:
            str: 生成的场景内容
        """
        self.logger.log("开始从大纲生成场景", 4)
        
        prompt = SCENE_OUTLINE_TO_SCENE.format(
            _SceneOutline=scene_outline,
            _Outline=story_outline,
            _BaseContext=base_context
        )
        
        scene = self.llm.generate(prompt)
        
        self.logger.log("场景生成完成", 4)
        return scene

def SceneOutlineToScene(Interface, _Logger, _ThisSceneOutline:str, _Outline:str, _BaseContext: str = ""):

    # Now we're finally going to go and write the scene provided.


    _Logger.Log(f"Starting SceneOutline->Scene", 2)
    MesssageHistory: list = []
    MesssageHistory.append(Interface.BuildSystemQuery(Writer.Prompts.DEFAULT_SYSTEM_PROMPT))
    MesssageHistory.append(Interface.BuildUserQuery(Writer.Prompts.SCENE_OUTLINE_TO_SCENE.format(_SceneOutline=_ThisSceneOutline, _Outline=_Outline)))

    Response = Interface.SafeGenerateText(_Logger, MesssageHistory, Writer.Config.CHAPTER_STAGE1_WRITER_MODEL, _MinWordCount=100)
    _Logger.Log(f"Finished SceneOutline->Scene", 5)

    return Interface.GetLastMessageText(Response)
