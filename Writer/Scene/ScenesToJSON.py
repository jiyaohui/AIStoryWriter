"""
场景转JSON模块
用于将场景描述转换为JSON格式
"""

from ..Prompts import SCENES_TO_JSON

class SceneJSONConverter:
    """
    场景JSON转换器类
    用于将场景描述转换为结构化的JSON格式
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
        
    def convert_to_json(self, scenes):
        """
        将场景描述转换为JSON
        
        参数:
            scenes (str): 场景描述文本
            
        返回:
            list: 场景JSON列表
        """
        self.logger.log("开始将场景转换为JSON格式", 4)
        
        prompt = SCENES_TO_JSON.format(_Scenes=scenes)
        response = self.llm.generate(prompt, format="json")
        
        try:
            scenes_list = self.llm.parse_json_response(response)
            self.logger.log("场景转换为JSON完成", 4)
            return scenes_list
        except Exception as e:
            self.logger.error(f"JSON转换失败: {str(e)}")
            return []
