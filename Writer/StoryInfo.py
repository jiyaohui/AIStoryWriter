"""
剧本信息模块
用于管理和处理剧本的元数据信息
"""

class ScriptInfo:
    """
    剧本信息类
    存储和管理剧本的基本信息
    """
    
    def __init__(self, title="", author="", genre=""):
        """
        初始化剧本信息
        
        参数:
            title (str): 剧本标题
            author (str): 编剧名
            genre (str): 剧本体裁
        """
        self.title = title
        self.author = author 
        self.genre = genre
        self.chapter_count = 0
        self.word_count = 0
        self.tags = []
        
    def add_tag(self, tag):
        """
        添加标签
        
        参数:
            tag (str): 要添加的标签
        """
        if tag not in self.tags:
            self.tags.append(tag)
            
    def update_stats(self, chapter_count, word_count):
        """
        更新统计信息
        
        参数:
            chapter_count (int): 场景数
            word_count (int): 总字数
        """
        self.chapter_count = chapter_count
        self.word_count = word_count
        
    def to_dict(self):
        """
        将信息转换为字典格式
        
        返回:
            dict: 包含剧本信息的字典
        """
        return {
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "chapter_count": self.chapter_count,
            "word_count": self.word_count,
            "tags": self.tags
        }
