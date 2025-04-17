"""
场景式章节生成模块
用于按场景生成章节内容
"""

import json
from ..Prompts import (
    CHAPTER_TO_SCENES,
    SCENES_TO_JSON,
    SCENE_OUTLINE_TO_SCENE
)

class SceneGenerator:
    """
    场景生成器类
    用于生成章节中的各个场景
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
        
    def generate_scenes(self, chapter_outline, story_outline):
        """
        将章节分解为场景并生成内容
        
        参数:
            chapter_outline (str): 章节大纲
            story_outline (str): 故事大纲
            
        返回:
            str: 生成的章节内容
        """
        # 获取场景大纲
        scenes_outline = self._get_scenes_outline(chapter_outline, story_outline)
        
        # 将场景大纲转换为JSON列表
        scenes_list = self._outline_to_json(scenes_outline)
        
        # 生成每个场景
        scenes_content = []
        for scene in scenes_list:
            content = self._generate_scene(scene, story_outline)
            scenes_content.append(content)
            
        # 合并所有场景
        return "\n\n".join(scenes_content)
        
    def _get_scenes_outline(self, chapter_outline, story_outline):
        """
        获取场景大纲
        
        参数:
            chapter_outline (str): 章节大纲
            story_outline (str): 故事大纲
            
        返回:
            str: 场景大纲
        """
        self.logger.log("生成场景大纲", 5)
        prompt = CHAPTER_TO_SCENES.format(
            _Outline=story_outline,
            _ThisChapter=chapter_outline
        )
        return self.llm.generate(prompt)
        
    def _outline_to_json(self, scenes_outline):
        """
        将场景大纲转换为JSON列表
        
        参数:
            scenes_outline (str): 场景大纲
            
        返回:
            list: 场景列表
        """
        self.logger.log("转换场景大纲为JSON格式", 5)
        prompt = SCENES_TO_JSON.format(_Scenes=scenes_outline)
        response = self.llm.generate(prompt, format="json")
        return self.llm.parse_json_response(response)
        
    def _generate_scene(self, scene_outline, story_outline):
        """
        生成单个场景内容
        
        参数:
            scene_outline (str): 场景大纲
            story_outline (str): 故事大纲
            
        返回:
            str: 生成的场景内容
        """
        self.logger.log("生成场景内容", 5)
        prompt = SCENE_OUTLINE_TO_SCENE.format(
            _SceneOutline=scene_outline,
            _Outline=story_outline
        )
        return self.llm.generate(prompt)
