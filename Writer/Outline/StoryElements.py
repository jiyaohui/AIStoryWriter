"""
故事元素模块
用于管理和生成故事的基本元素
"""

class StoryElements:
    """
    故事元素类
    管理故事的基本构成元素
    """
    
    def __init__(self):
        """
        初始化故事元素
        """
        self.characters = []
        self.settings = []
        self.themes = []
        self.conflicts = []
        
    def add_character(self, name, description):
        """
        添加角色
        
        参数:
            name (str): 角色名称
            description (str): 角色描述
        """
        self.characters.append({
            "name": name,
            "description": description
        })
        
    def add_setting(self, location, description):
        """
        添加场景设定
        
        参数:
            location (str): 地点名称
            description (str): 地点描述
        """
        self.settings.append({
            "location": location,
            "description": description
        })
        
    def add_theme(self, theme):
        """
        添加主题
        
        参数:
            theme (str): 主题描述
        """
        if theme not in self.themes:
            self.themes.append(theme)
            
    def add_conflict(self, conflict_type, description):
        """
        添加冲突
        
        参数:
            conflict_type (str): 冲突类型
            description (str): 冲突描述
        """
        self.conflicts.append({
            "type": conflict_type,
            "description": description
        })
        
    def to_markdown(self):
        """
        将故事元素转换为markdown格式
        
        返回:
            str: markdown格式的故事元素描述
        """
        md = "# 故事元素\n\n"
        
        md += "## 角色\n"
        for char in self.characters:
            md += f"- {char['name']}: {char['description']}\n"
            
        md += "\n## 场景设定\n"
        for setting in self.settings:
            md += f"- {setting['location']}: {setting['description']}\n"
            
        md += "\n## 主题\n"
        for theme in self.themes:
            md += f"- {theme}\n"
            
        md += "\n## 冲突\n"
        for conflict in self.conflicts:
            md += f"- {conflict['type']}: {conflict['description']}\n"
            
        return md
