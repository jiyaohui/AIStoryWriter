"""
大纲生成器模块
用于生成和管理故事大纲
"""

import Writer.LLMEditor
import Writer.PrintUtils
import Writer.Config
import Writer.Outline.StoryElements
import Writer.Prompts

from .Prompts import INITIAL_OUTLINE_PROMPT, OUTLINE_REVISION_PROMPT

# We should probably do outline generation in stages, allowing us to go back and add foreshadowing, etc back to previous segments


def GenerateOutline(Interface, _Logger, _OutlinePrompt, _QualityThreshold: int = 85):

    # Get any important info about the base prompt to pass along
    Prompt: str = Writer.Prompts.GET_IMPORTANT_BASE_PROMPT_INFO.format(
        _Prompt = _OutlinePrompt
    )


    _Logger.Log(f"Extracting Important Base Context", 4)
    Messages = [Interface.BuildUserQuery(Prompt)]
    Messages = Interface.SafeGenerateText(
        _Logger, Messages, Writer.Config.INITIAL_OUTLINE_WRITER_MODEL
    )
    BaseContext: str = Interface.GetLastMessageText(Messages)
    _Logger.Log(f"Done Extracting Important Base Context", 4)


    # Generate Story Elements
    StoryElements: str = Writer.Outline.StoryElements.GenerateStoryElements(
        Interface, _Logger, _OutlinePrompt
    )


    # Now, Generate Initial Outline
    Prompt: str = Writer.Prompts.INITIAL_OUTLINE_PROMPT.format(
        StoryElements=StoryElements, _OutlinePrompt=_OutlinePrompt
    )


    _Logger.Log(f"Generating Initial Outline", 4)
    Messages = [Interface.BuildUserQuery(Prompt)]
    Messages = Interface.SafeGenerateText(
        _Logger, Messages, Writer.Config.INITIAL_OUTLINE_WRITER_MODEL, _MinWordCount=250
    )
    Outline: str = Interface.GetLastMessageText(Messages)
    _Logger.Log(f"Done Generating Initial Outline", 4)

    _Logger.Log(f"Entering Feedback/Revision Loop", 3)
    WritingHistory = Messages
    Rating: int = 0
    Iterations: int = 0
    while True:
        Iterations += 1
        Feedback = Writer.LLMEditor.GetFeedbackOnOutline(Interface, _Logger, Outline)
        Rating = Writer.LLMEditor.GetOutlineRating(Interface, _Logger, Outline)
        # Rating has been changed from a 0-100 int, to does it meet the standards (yes/no)?
        # Yes it has - the 0-100 int isn't actually good at all, LLM just returned a bunch of junk ratings

        if Iterations > Writer.Config.OUTLINE_MAX_REVISIONS:
            break
        if (Iterations > Writer.Config.OUTLINE_MIN_REVISIONS) and (Rating == True):
            break

        Outline = ReviseOutline(Interface, _Logger, Outline, Feedback)

    _Logger.Log(f"Quality Standard Met, Exiting Feedback/Revision Loop", 4)

    # Generate Final Outline
    FinalOutline: str = f"""
{BaseContext}

{StoryElements}

{Outline}
    """

    return FinalOutline, StoryElements, Outline, BaseContext


def ReviseOutline(Interface, _Logger, _Outline, _Feedback, _History: list = []):

    RevisionPrompt: str = Writer.Prompts.OUTLINE_REVISION_PROMPT.format(
        _Outline=_Outline, _Feedback=_Feedback
    )

    _Logger.Log(f"Revising Outline", 2)
    Messages = _History
    Messages.append(Interface.BuildUserQuery(RevisionPrompt))
    Messages = Interface.SafeGenerateText(
        _Logger, Messages, Writer.Config.INITIAL_OUTLINE_WRITER_MODEL, _MinWordCount=250
    )
    SummaryText: str = Interface.GetLastMessageText(Messages)
    _Logger.Log(f"Done Revising Outline", 2)

    return SummaryText, Messages


def GeneratePerChapterOutline(Interface, _Logger, _Chapter, _Outline:str, _History: list = []):

    RevisionPrompt: str = Writer.Prompts.CHAPTER_OUTLINE_PROMPT.format(
        _Chapter=_Chapter,
        _Outline=_Outline
    )
    _Logger.Log("Generating Outline For Chapter " + str(_Chapter), 5)
    Messages = _History
    Messages.append(Interface.BuildUserQuery(RevisionPrompt))
    Messages = Interface.SafeGenerateText(
        _Logger, Messages, Writer.Config.CHAPTER_OUTLINE_WRITER_MODEL, _MinWordCount=50
    )
    SummaryText: str = Interface.GetLastMessageText(Messages)
    _Logger.Log("Done Generating Outline For Chapter " + str(_Chapter), 5)

    return SummaryText, Messages


class OutlineGenerator:
    """
    大纲生成器类
    处理故事大纲的生成和修改
    """
    
    def __init__(self, llm_editor):
        """
        初始化大纲生成器
        
        参数:
            llm_editor: LLM编辑器实例
        """
        self.llm = llm_editor
        
    def generate_initial(self, prompt, elements):
        """
        生成初始大纲
        
        参数:
            prompt (str): 故事提示
            elements (str): 故事元素
            
        返回:
            str: 生成的大纲
        """
        prompt = INITIAL_OUTLINE_PROMPT.format(
            _OutlinePrompt=prompt,
            StoryElements=elements
        )
        return self.llm.generate(prompt)
        
    def revise_outline(self, outline, feedback):
        """
        根据反馈修改大纲
        
        参数:
            outline (str): 当前大纲
            feedback (str): 修改反馈
            
        返回:
            str: 修改后的大纲
        """
        prompt = OUTLINE_REVISION_PROMPT.format(
            _Outline=outline,
            _Feedback=feedback
        )
        return self.llm.generate(prompt)
