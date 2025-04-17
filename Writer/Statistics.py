"""
统计模块
用于计算和分析剧本的各种统计数据
"""

import re
from .Prompts import STATS_PROMPT

def get_word_count(text):
    """
    计算文本的字数
    
    参数:
        text (str): 要计算的文本
        
    返回:
        int: 字数统计
    """
    words = text.split()
    return len(words)

def get_scene_stats(scene):
    """
    获取单个场景的统计信息
    
    参数:
        scene (str): 场景内容
        
    返回:
        dict: 包含统计信息的字典
    """
    stats = {
        "word_count": get_word_count(scene),
        "paragraph_count": len(scene.split("\n\n")),
        "dialogue_count": len(re.findall(r'"[^"]*"', scene))
    }
    return stats

def analyze_script(llm, script_text):
    """
    分析整个剧本并生成统计报告
    
    参数:
        llm: LLM编辑器实例
        script_text (str): 剧本全文
        
    返回:
        dict: 包含分析结果的字典
    """
    prompt = STATS_PROMPT.format(_Script=script_text)
    response = llm.generate(prompt)
    
    # 解析LLM的JSON响应
    try:
        stats = json.loads(response)
        stats["total_words"] = get_word_count(script_text)
        return stats
    except json.JSONDecodeError:
        return {"error": "无法解析统计数据"}