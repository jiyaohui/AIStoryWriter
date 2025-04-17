"""
文本清理模块
用于清理和格式化剧本内容
"""

class TextScrubber:
    """
    文本清理器类
    用于删除不必要的标记和格式化文本
    """
    
    def __init__(self):
        """
        初始化文本清理器
        """
        self.markdown_markers = [
            "#",
            "*",
            "_",
            "`",
            "-"
        ]
        
    def clean_scene(self, scene_text):
        """
        清理场景文本
        
        参数:
            scene_text (str): 要清理的场景文本
            
        返回:
            str: 清理后的文本
        """
        # 删除markdown标记
        cleaned = scene_text
        for marker in self.markdown_markers:
            cleaned = cleaned.replace(marker, "")
            
        # 删除多余的空行
        cleaned = "\n".join(line for line in cleaned.split("\n") if line.strip())
        
        return cleaned.strip()
        
    def format_scene(self, scene_text, scene_num):
        """
        格式化场景文本
        
        参数:
            scene_text (str): 要格式化的场景文本
            scene_num (int): 场景编号
            
        返回:
            str: 格式化后的文本
        """
        # 添加场景标题
        formatted = f"第{scene_num}场\n\n"
        formatted += self.clean_scene(scene_text)
        
        return formatted
