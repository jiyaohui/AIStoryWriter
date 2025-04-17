"""
配置模块
存储全局配置参数
"""

# LLM模型配置
CHAPTER_WRITER_MODEL = "gpt-4"  # 章节生成模型
INITIAL_OUTLINE_WRITER_MODEL = "gpt-4"  # 初始大纲生成模型
CHAPTER_OUTLINE_WRITER_MODEL = "gpt-4"  # 章节大纲生成模型
REVISION_MODEL = "gpt-4"  # 修改模型
EVAL_MODEL = "gpt-4"  # 评估模型
TRANSLATOR_MODEL = "gpt-4"  # 翻译模型
SCRUB_MODEL = "gpt-4"  # 清理模型
INFO_MODEL = "gpt-4"  # 信息提取模型

# 生成参数配置
OUTLINE_MIN_REVISIONS = 2  # 大纲最小修改次数
OUTLINE_MAX_REVISIONS = 5  # 大纲最大修改次数
CHAPTER_MIN_REVISIONS = 2  # 章节最小修改次数
CHAPTER_MAX_REVISIONS = 5  # 章节最大修改次数

# 日志配置
DEFAULT_LOG_LEVEL = 5  # 默认日志级别

# 输出配置
OUTPUT_DIR = "output"  # 输出目录
CHAPTER_FILE_PREFIX = "chapter_"  # 章节文件前缀
OUTLINE_FILE_NAME = "outline.md"  # 大纲文件名

CHAPTER_STAGE1_WRITER_MODEL = "ollama://llama3:70b"  # Note this value is overridden by the argparser
CHAPTER_STAGE2_WRITER_MODEL = "ollama://llama3:70b"  # Note this value is overridden by the argparser
CHAPTER_STAGE3_WRITER_MODEL = "ollama://llama3:70b"  # Note this value is overridden by the argparser
CHAPTER_STAGE4_WRITER_MODEL = "ollama://llama3:70b"  # Note this value is overridden by the argparser
CHAPTER_REVISION_WRITER_MODEL = (
    "ollama://llama3:70b"  # Note this value is overridden by the argparser
)

OLLAMA_CTX = 8192

OLLAMA_HOST = "127.0.0.1:11434"

SEED = 12  # Note this value is overridden by the argparser

TRANSLATE_LANGUAGE = ""  # If the user wants to translate, this'll be changed from empty to a language e.g 'French' or 'Russian'
TRANSLATE_PROMPT_LANGUAGE = ""  # If the user wants to translate their prompt, this'll be changed from empty to a language e.g 'French' or 'Russian'

OUTLINE_QUALITY = 87  # Note this value is overridden by the argparser
CHAPTER_NO_REVISIONS = True  # Note this value is overridden by the argparser # disables all revision checks for the chapter, overriding any other chapter quality/revision settings
CHAPTER_QUALITY = 85  # Note this value is overridden by the argparser

SCRUB_NO_SCRUB = False  # Note this value is overridden by the argparser
EXPAND_OUTLINE = False  # Note this value is overridden by the argparser
ENABLE_FINAL_EDIT_PASS = False  # Note this value is overridden by the argparser

SCENE_GENERATION_PIPELINE = True

OPTIONAL_OUTPUT_NAME = ""

DEBUG = False

# Tested models:
"llama3:70b"  # works as editor model, DO NOT use as writer model, it sucks
"vanilj/midnight-miqu-70b-v1.5"  # works rather well as the writer, not well as anything else
"command-r"
"qwen:72b"
"command-r-plus"
"nous-hermes2"  # not big enough to really do a good job - do not use
"dbrx"  # sucks - do not use
