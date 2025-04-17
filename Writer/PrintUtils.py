"""
打印工具模块
用于格式化和输出文本内容
"""

import termcolor
import datetime
import os
import json
import sys
from typing import List


def PrintMessageHistory(_Messages):
    print("------------------------------------------------------------")
    for Message in _Messages:
        print(Message)
    print("------------------------------------------------------------")


class Logger:
    """
    日志记录器类
    用于记录和输出日志信息
    """
    
    def __init__(self, log_level=5):
        """
        初始化日志记录器
        
        参数:
            log_level (int): 日志级别(1-10)
        """
        self.log_level = log_level
        
    def log(self, message, level=5):
        """
        记录日志消息
        
        参数:
            message (str): 日志消息
            level (int): 消息级别
        """
        if level >= self.log_level:
            print(f"[LOG {level}] {message}")
            
    def error(self, message):
        """
        记录错误消息
        
        参数:
            message (str): 错误消息
        """
        print(f"[ERROR] {message}", file=sys.stderr)


    def __init__(self, _LogfilePrefix="Logs"):

        # Make Paths For Log
        LogDirPath = _LogfilePrefix + "/Generation_" + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        os.makedirs(LogDirPath + "/LangchainDebug", exist_ok=True)

        # Setup Log Path
        self.LogDirPrefix = LogDirPath
        self.LogPath = LogDirPath + "/Main.log"
        self.File = open(self.LogPath, "a")
        self.LangchainID = 0

        self.LogItems = []


    # Helper function that saves the entire language chain object as both json and markdown for debugging later
    def SaveLangchain(self, _LangChainID:str, _LangChain:list):

        # Calculate Filepath For This Langchain
        ThisLogPathJSON:str = self.LogDirPrefix + f"/LangchainDebug/{self.LangchainID}_{_LangChainID}.json"
        ThisLogPathMD:str = self.LogDirPrefix + f"/LangchainDebug/{self.LangchainID}_{_LangChainID}.md"
        LangChainDebugTitle:str = f"{self.LangchainID}_{_LangChainID}"
        self.LangchainID += 1

        # Generate and Save JSON Version
        with open(ThisLogPathJSON, "w") as f:
            f.write(json.dumps(_LangChain, indent=4, sort_keys=True))
        
        # Now, Save Markdown Version
        with open(ThisLogPathMD, "w") as f:
            MarkdownVersion:str = f"# Debug LangChain {LangChainDebugTitle}\n**Note: '```' tags have been removed in this version.**\n"
            for Message in _LangChain:
                MarkdownVersion += f"\n\n\n# Role: {Message['role']}\n"
                MarkdownVersion += f"```{Message['content'].replace('```', '')}```"
            f.write(MarkdownVersion)
        
        self.log(f"Wrote This Language Chain ({LangChainDebugTitle}) To Debug File {ThisLogPathMD}", 5)


    # Saves the given story to disk
    def SaveStory(self, _StoryContent:str):

        with open(f"{self.LogDirPrefix}/Story.md", "w") as f:
            f.write(_StoryContent)

        self.log(f"Wrote Story To Disk At {self.LogDirPrefix}/Story.md", 5)


    # Logs an item
    def Log(self, _Item, _Level:int):

        # Create Log Entry
        LogEntry = f"[{str(_Level).ljust(2)}] [{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}] {_Item}"

        # Write it to file
        self.File.write(LogEntry + "\n")
        self.LogItems.append(LogEntry)

        # Now color and print it
        if (_Level == 0):
            LogEntry = termcolor.colored(LogEntry, "white")
        elif (_Level == 1):
            LogEntry = termcolor.colored(LogEntry, "grey")
        elif (_Level == 2):
            LogEntry = termcolor.colored(LogEntry, "blue")
        elif (_Level == 3):
            LogEntry = termcolor.colored(LogEntry, "cyan")
        elif (_Level == 4):
            LogEntry = termcolor.colored(LogEntry, "magenta")
        elif (_Level == 5):
            LogEntry = termcolor.colored(LogEntry, "green")
        elif (_Level == 6):
            LogEntry = termcolor.colored(LogEntry, "yellow")
        elif (_Level == 7):
            LogEntry = termcolor.colored(LogEntry, "red")

        print(LogEntry)



    def __del__(self):
        self.File.close()


def clear_screen():
    """
    清除终端屏幕
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    
def print_divider():
    """
    打印分隔线
    """
    print("-" * 80)
    
def print_chapter(chapter_num: int, content: str):
    """
    格式化打印章节内容
    
    参数:
        chapter_num (int): 章节编号
        content (str): 章节内容
    """
    print_divider()
    print(f"\n第{chapter_num}章\n")
    print(content)
    print_divider()
    
def print_outline(outline: str):
    """
    格式化打印大纲
    
    参数:
        outline (str): 大纲内容
    """
    print_divider()
    print("\n故事大纲\n")
    print(outline)
    print_divider()
    
def format_messages(messages: List[dict]) -> str:
    """
    格式化消息列表
    
    参数:
        messages (List[dict]): 消息列表
        
    返回:
        str: 格式化后的消息文本
    """
    formatted = ""
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        formatted += f"\n[{role}]\n{content}\n"
    return formatted.strip()