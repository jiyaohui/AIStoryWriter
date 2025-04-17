"""
场景生成器模块
用于生成和管理剧本场景
"""

import json

import Writer.LLMEditor
import Writer.PrintUtils
import Writer.Config
import Writer.Chapter.ChapterGenSummaryCheck
import Writer.Prompts

import Writer.Scene.ChapterByScene

from ..Prompts import (
    CHAPTER_GENERATION_STAGE1,
    CHAPTER_GENERATION_STAGE2,
    CHAPTER_GENERATION_STAGE3,
    CHAPTER_GENERATION_STAGE4
)

def GenerateChapter(
    Interface,
    _Logger,
    _ChapterNum: int,
    _TotalChapters: int,
    _Outline: str,
    _Chapters: list = [],
    _QualityThreshold: int = 85,
    _BaseContext:str = ""
):

    # Some important notes
    # We're going to remind the author model of the previous chapters here, so it knows what has been written before.

    #### Stage 0: Create base language chain
    _Logger.Log(f"Creating Base Langchain For Chapter {_ChapterNum} Generation", 2)
    MesssageHistory: list = []
    MesssageHistory.append(
        Interface.BuildSystemQuery(
            Writer.Prompts.CHAPTER_GENERATION_INTRO.format(
                _ChapterNum=_ChapterNum, _TotalChapters=_TotalChapters
            )
        )
    )

    ContextHistoryInsert: str = ""

    if len(_Chapters) > 0:

        ChapterSuperlist: str = ""
        for Chapter in _Chapters:
            ChapterSuperlist += f"{Chapter}\n"

        ContextHistoryInsert += Writer.Prompts.CHAPTER_HISTORY_INSERT.format(
            _Outline=_Outline, ChapterSuperlist=ChapterSuperlist
        )

    #
    # MesssageHistory.append(Interface.BuildUserQuery(f"""
    # Here is the novel so far.
    # """))
    # MesssageHistory.append(Interface.BuildUserQuery(ChapterSuperlist))
    # MesssageHistory.append(Interface.BuildSystemQuery("Make sure to pay attention to the content that has happened in these previous chapters. It's okay to deviate from the outline a little in order to ensure you continue the same story from previous chapters."))

    # Now, extract the this-chapter-outline segment
    _Logger.Log(f"Extracting Chapter Specific Outline", 4)
    ThisChapterOutline: str = ""
    ChapterSegmentMessages = []
    ChapterSegmentMessages.append(
        Interface.BuildSystemQuery(Writer.Prompts.CHAPTER_GENERATION_INTRO)
    )
    ChapterSegmentMessages.append(
        Interface.BuildUserQuery(
            Writer.Prompts.CHAPTER_GENERATION_PROMPT.format(
                _Outline=_Outline, _ChapterNum=_ChapterNum
            )
        )
    )
    ChapterSegmentMessages = Interface.SafeGenerateText(
        _Logger,
        ChapterSegmentMessages,
        Writer.Config.CHAPTER_STAGE1_WRITER_MODEL, _MinWordCount=120
    )  # CHANGE THIS MODEL EVENTUALLY - BUT IT WORKS FOR NOW!!!
    ThisChapterOutline: str = Interface.GetLastMessageText(ChapterSegmentMessages)
    _Logger.Log(f"Created Chapter Specific Outline", 4)

    # Generate Summary of Last Chapter If Applicable
    FormattedLastChapterSummary: str = ""
    if len(_Chapters) > 0:
        _Logger.Log(f"Creating Summary Of Last Chapter Info", 3)
        ChapterSummaryMessages = []
        ChapterSummaryMessages.append(
            Interface.BuildSystemQuery(Writer.Prompts.CHAPTER_SUMMARY_INTRO)
        )
        ChapterSummaryMessages.append(
            Interface.BuildUserQuery(
                Writer.Prompts.CHAPTER_SUMMARY_PROMPT.format(
                    _ChapterNum=_ChapterNum,
                    _TotalChapters=_TotalChapters,
                    _Outline=_Outline,
                    _LastChapter=_Chapters[-1],
                )
            )
        )
        ChapterSummaryMessages = Interface.SafeGenerateText(
            _Logger,
            ChapterSummaryMessages,
            Writer.Config.CHAPTER_STAGE1_WRITER_MODEL, _MinWordCount=100
        )  # CHANGE THIS MODEL EVENTUALLY - BUT IT WORKS FOR NOW!!!
        FormattedLastChapterSummary: str = Interface.GetLastMessageText(
            ChapterSummaryMessages
        )
        _Logger.Log(f"Created Summary Of Last Chapter Info", 3)

    DetailedChapterOutline: str = ThisChapterOutline
    if FormattedLastChapterSummary != "":
        DetailedChapterOutline = ThisChapterOutline

    _Logger.Log(f"Done with base langchain setup", 2)


    # If scene generation disabled, use the normal initial plot generator
    Stage1Chapter = ""
    if (not Writer.Config.SCENE_GENERATION_PIPELINE):

        #### STAGE 1: Create Initial Plot
        IterCounter: int = 0
        Feedback: str = ""
        while True:
            Prompt = Writer.Prompts.CHAPTER_GENERATION_STAGE1.format(
                ContextHistoryInsert=ContextHistoryInsert,
                _ChapterNum=_ChapterNum,
                _TotalChapters=_TotalChapters,
                ThisChapterOutline=ThisChapterOutline,
                FormattedLastChapterSummary=FormattedLastChapterSummary,
                Feedback=Feedback,
                _BaseContext=_BaseContext
            )

            # Generate Initial Chapter
            _Logger.Log(
                f"Generating Initial Chapter (Stage 1: Plot) {_ChapterNum}/{_TotalChapters} (Iteration {IterCounter})",
                5,
            )
            Messages = MesssageHistory.copy()
            Messages.append(Interface.BuildUserQuery(Prompt))

            Messages = Interface.SafeGenerateText(
                _Logger,
                Messages,
                Writer.Config.CHAPTER_STAGE1_WRITER_MODEL,
                _SeedOverride=IterCounter + Writer.Config.SEED,
                _MinWordCount=100
            )
            IterCounter += 1
            Stage1Chapter: str = Interface.GetLastMessageText(Messages)
            _Logger.Log(
                f"Finished Initial Generation For Initial Chapter (Stage 1: Plot)  {_ChapterNum}/{_TotalChapters}",
                5,
            )

            # Check if LLM did the work
            if IterCounter > Writer.Config.CHAPTER_MAX_REVISIONS:
                _Logger.Log(
                    "Chapter Summary-Based Revision Seems Stuck - Forcefully Exiting", 7
                )
                break
            Result, Feedback = Writer.Chapter.ChapterGenSummaryCheck.LLMSummaryCheck(
                Interface, _Logger, DetailedChapterOutline, Stage1Chapter
            )
            if Result:
                _Logger.Log(
                    f"Done Generating Initial Chapter (Stage 1: Plot)  {_ChapterNum}/{_TotalChapters}",
                    5,
                )
                break
    
    else:

        Stage1Chapter = Writer.Scene.ChapterByScene.ChapterByScene(Interface, _Logger, ThisChapterOutline, _Outline, _BaseContext)


    #### STAGE 2: Add Character Development
    Stage2Chapter = ""
    IterCounter: int = 0
    Feedback: str = ""
    while True:
        Prompt = Writer.Prompts.CHAPTER_GENERATION_STAGE2.format(
            ContextHistoryInsert=ContextHistoryInsert,
            _ChapterNum=_ChapterNum,
            _TotalChapters=_TotalChapters,
            ThisChapterOutline=ThisChapterOutline,
            FormattedLastChapterSummary=FormattedLastChapterSummary,
            Stage1Chapter=Stage1Chapter,
            Feedback=Feedback,
            _BaseContext=_BaseContext
        )

        # Generate Initial Chapter
        _Logger.Log(
            f"Generating Initial Chapter (Stage 2: Character Development) {_ChapterNum}/{_TotalChapters} (Iteration {IterCounter})",
            5,
        )
        Messages = MesssageHistory.copy()
        Messages.append(Interface.BuildUserQuery(Prompt))

        Messages = Interface.SafeGenerateText(
            _Logger,
            Messages,
            Writer.Config.CHAPTER_STAGE2_WRITER_MODEL,
            _SeedOverride=IterCounter + Writer.Config.SEED,
            _MinWordCount=100
        )
        IterCounter += 1
        Stage2Chapter: str = Interface.GetLastMessageText(Messages)
        _Logger.Log(
            f"Finished Initial Generation For Initial Chapter (Stage 2: Character Development)  {_ChapterNum}/{_TotalChapters}",
            5,
        )

        # Check if LLM did the work
        if IterCounter > Writer.Config.CHAPTER_MAX_REVISIONS:
            _Logger.Log(
                "Chapter Summary-Based Revision Seems Stuck - Forcefully Exiting", 7
            )
            break
        Result, Feedback = Writer.Chapter.ChapterGenSummaryCheck.LLMSummaryCheck(
            Interface, _Logger, DetailedChapterOutline, Stage2Chapter
        )
        if Result:
            _Logger.Log(
                f"Done Generating Initial Chapter (Stage 2: Character Development)  {_ChapterNum}/{_TotalChapters}",
                5,
            )
            break

    #### STAGE 3: Add Dialogue
    Stage3Chapter = ""
    IterCounter: int = 0
    Feedback: str = ""
    while True:
        Prompt = Writer.Prompts.CHAPTER_GENERATION_STAGE3.format(
            ContextHistoryInsert=ContextHistoryInsert,
            _ChapterNum=_ChapterNum,
            _TotalChapters=_TotalChapters,
            ThisChapterOutline=ThisChapterOutline,
            FormattedLastChapterSummary=FormattedLastChapterSummary,
            Stage2Chapter=Stage2Chapter,
            Feedback=Feedback,
            _BaseContext=_BaseContext
        )
        # Generate Initial Chapter
        _Logger.Log(
            f"Generating Initial Chapter (Stage 3: Dialogue) {_ChapterNum}/{_TotalChapters} (Iteration {IterCounter})",
            5,
        )
        Messages = MesssageHistory.copy()
        Messages.append(Interface.BuildUserQuery(Prompt))

        Messages = Interface.SafeGenerateText(
            _Logger,
            Messages,
            Writer.Config.CHAPTER_STAGE3_WRITER_MODEL,
            _SeedOverride=IterCounter + Writer.Config.SEED,
            _MinWordCount=100
        )
        IterCounter += 1
        Stage3Chapter: str = Interface.GetLastMessageText(Messages)
        _Logger.Log(
            f"Finished Initial Generation For Initial Chapter (Stage 3: Dialogue)  {_ChapterNum}/{_TotalChapters}",
            5,
        )

        # Check if LLM did the work
        if IterCounter > Writer.Config.CHAPTER_MAX_REVISIONS:
            _Logger.Log(
                "Chapter Summary-Based Revision Seems Stuck - Forcefully Exiting", 7
            )
            break
        Result, Feedback = Writer.Chapter.ChapterGenSummaryCheck.LLMSummaryCheck(
            Interface, _Logger, DetailedChapterOutline, Stage3Chapter
        )
        if Result:
            _Logger.Log(
                f"Done Generating Initial Chapter (Stage 3: Dialogue)  {_ChapterNum}/{_TotalChapters}",
                5,
            )
            break

        #     #### STAGE 4: Final-Pre-Revision Edit Pass
        # Prompt = Writer.Prompts.CHAPTER_GENERATION_STAGE4.format(
        #    ContextHistoryInsert=ContextHistoryInsert,
        #     _ChapterNum=_ChapterNum,
        #     _TotalChapters=_TotalChapters,
        #     _Outline=_Outline,
        #     Stage3Chapter=Stage3Chapter,
        #     Feedback=Feedback,
        # )

    #     # Generate Initial Chapter
    #     _Logger.Log(f"Generating Initial Chapter (Stage 4: Final Pass) {_ChapterNum}/{_TotalChapters}", 5)
    #     Messages = MesssageHistory.copy()
    #     Messages.append(Interface.BuildUserQuery(Prompt))

    #     Messages = Interface.SafeGenerateText(_Logger, Messages, Writer.Config.CHAPTER_STAGE4_WRITER_MODEL)
    #     Chapter:str = Interface.GetLastMessageText(Messages)
    #     _Logger.Log(f"Done Generating Initial Chapter (Stage 4: Final Pass)  {_ChapterNum}/{_TotalChapters}", 5)
    Chapter: str = Stage3Chapter

    #### Stage 5: Revision Cycle
    if Writer.Config.CHAPTER_NO_REVISIONS:
        _Logger.Log(f"Chapter Revision Disabled In Config, Exiting Now", 5)
        return Chapter

    _Logger.Log(
        f"Entering Feedback/Revision Loop (Stage 5) For Chapter {_ChapterNum}/{_TotalChapters}",
        4,
    )
    WritingHistory = MesssageHistory.copy()
    Rating: int = 0
    Iterations: int = 0
    while True:
        Iterations += 1
        Feedback = Writer.LLMEditor.GetFeedbackOnChapter(
            Interface, _Logger, Chapter, _Outline
        )
        Rating = Writer.LLMEditor.GetChapterRating(Interface, _Logger, Chapter)

        if Iterations > Writer.Config.CHAPTER_MAX_REVISIONS:
            break
        if (Iterations > Writer.Config.CHAPTER_MIN_REVISIONS) and (Rating == True):
            break
        Chapter, WritingHistory = ReviseChapter(
            Interface, _Logger, Chapter, Feedback, WritingHistory
        )

    _Logger.Log(
        f"Quality Standard Met, Exiting Feedback/Revision Loop (Stage 5) For Chapter {_ChapterNum}/{_TotalChapters}",
        4,
    )

    return Chapter


def ReviseChapter(Interface, _Logger, _Chapter, _Feedback, _History: list = []):

    RevisionPrompt = Writer.Prompts.CHAPTER_REVISION.format(
        _Chapter=_Chapter, _Feedback=_Feedback
    )

    _Logger.Log("Revising Chapter", 5)
    Messages = _History
    Messages.append(Interface.BuildUserQuery(RevisionPrompt))
    Messages = Interface.SafeGenerateText(
        _Logger, Messages, Writer.Config.CHAPTER_REVISION_WRITER_MODEL,
        _MinWordCount=100
    )
    SummaryText: str = Interface.GetLastMessageText(Messages)
    _Logger.Log("Done Revising Chapter", 5)

    return SummaryText, Messages

class SceneGenerator:
    """
    场景生成器类
    处理场景的生成和修改
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
        
    def generate_chapter(self, chapter_num, outline, previous_chapters=None):
        """
        生成单个场景
        
        参数:
            chapter_num (int): 场景编号
            outline (str): 故事大纲
            previous_chapters (list): 之前的场景列表
            
        返回:
            str: 生成的场景内容
        """
        self.logger.log(f"开始生成第{chapter_num}场景", 4)
        
        # 第1阶段：生成基本情节
        chapter = self._generate_stage1(chapter_num, outline, previous_chapters)
        
        # 第2阶段：添加角色发展
        chapter = self._generate_stage2(chapter, chapter_num, outline)
        
        # 第3阶段：添加对话
        chapter = self._generate_stage3(chapter, chapter_num, outline)
        
        # 第4阶段：最终润色
        chapter = self._generate_stage4(chapter, outline)
        
        self.logger.log(f"第{chapter_num}场景生成完成", 4)
        return chapter
        
    def _generate_stage1(self, chapter_num, outline, previous_chapters):
        """
        生成第1阶段：基本情节
        
        参数:
            chapter_num (int): 场景编号
            outline (str): 故事大纲
            previous_chapters (list): 之前的场景
            
        返回:
            str: 生成的内容
        """
        self.logger.log("生成基本情节", 5)
        prompt = CHAPTER_GENERATION_STAGE1.format(
            _ChapterNum=chapter_num,
            _Outline=outline,
            ChapterSuperlist=previous_chapters
        )
        return self.llm.generate(prompt, model="chapter_stage1")
        
    def _generate_stage2(self, chapter, chapter_num, outline):
        """
        生成第2阶段：角色发展
        
        参数:
            chapter (str): 第1阶段的内容
            chapter_num (int): 场景编号
            outline (str): 故事大纲
            
        返回:
            str: 生成的内容
        """
        self.logger.log("添加角色发展", 5)
        prompt = CHAPTER_GENERATION_STAGE2.format(
            _ChapterNum=chapter_num,
            _Outline=outline,
            Stage1Chapter=chapter
        )
        return self.llm.generate(prompt, model="chapter_stage2")
        
    def _generate_stage3(self, chapter, chapter_num, outline):
        """
        生成第3阶段：对话
        
        参数:
            chapter (str): 第2阶段的内容
            chapter_num (int): 场景编号
            outline (str): 故事大纲
            
        返回:
            str: 生成的内容
        """
        self.logger.log("添加对话", 5)
        prompt = CHAPTER_GENERATION_STAGE3.format(
            _ChapterNum=chapter_num,
            _Outline=outline,
            Stage2Chapter=chapter
        )
        return self.llm.generate(prompt, model="chapter_stage3")
        
    def _generate_stage4(self, chapter, outline):
        """
        生成第4阶段：最终润色
        
        参数:
            chapter (str): 第3阶段的内容
            outline (str): 故事大纲
            
        返回:
            str: 生成的内容
        """
        self.logger.log("进行最终润色", 5)
        prompt = CHAPTER_GENERATION_STAGE4.format(
            _Outline=outline,
            Stage3Chapter=chapter
        )
        return self.llm.generate(prompt, model="chapter_stage4")
