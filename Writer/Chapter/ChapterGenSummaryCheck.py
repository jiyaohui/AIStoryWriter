import json

import Writer.LLMEditor
import Writer.PrintUtils
import Writer.Config
import Writer.Prompts

from ..Prompts import (
    SUMMARY_CHECK_INTRO,
    SUMMARY_CHECK_PROMPT,
    SUMMARY_OUTLINE_INTRO,
    SUMMARY_OUTLINE_PROMPT,
    SUMMARY_COMPARE_INTRO,
    SUMMARY_COMPARE_PROMPT
)


def LLMSummaryCheck(Interface, _Logger, _RefSummary: str, _Work: str):
    """
    Generates a summary of the work provided, and compares that to the reference summary, asking if they answered the prompt correctly.
    """

    # LLM Length Check - Firstly, check if the length of the response was at least 100 words.
    if len(_Work.split(" ")) < 100:
        _Logger.Log(
            "Previous response didn't meet the length requirement, so it probably tried to cheat around writing.",
            7,
        )
        return False, ""

    # Build Summariziation Langchain
    SummaryLangchain: list = []
    SummaryLangchain.append(
        Interface.BuildSystemQuery(SUMMARY_CHECK_INTRO)
    )
    SummaryLangchain.append(
        Interface.BuildUserQuery(
            SUMMARY_CHECK_PROMPT.format(_Work=_Work)
        )
    )
    SummaryLangchain = Interface.SafeGenerateText(
        _Logger, SummaryLangchain, Writer.Config.CHAPTER_STAGE1_WRITER_MODEL
    )  # CHANGE THIS MODEL EVENTUALLY - BUT IT WORKS FOR NOW!!!
    WorkSummary: str = Interface.GetLastMessageText(SummaryLangchain)

    # Now Summarize The Outline
    SummaryLangchain: list = []
    SummaryLangchain.append(
        Interface.BuildSystemQuery(SUMMARY_OUTLINE_INTRO)
    )
    SummaryLangchain.append(
        Interface.BuildUserQuery(
            SUMMARY_OUTLINE_PROMPT.format(_RefSummary=_RefSummary)
        )
    )
    SummaryLangchain = Interface.SafeGenerateText(
        _Logger, SummaryLangchain, Writer.Config.CHAPTER_STAGE1_WRITER_MODEL
    )  # CHANGE THIS MODEL EVENTUALLY - BUT IT WORKS FOR NOW!!!
    OutlineSummary: str = Interface.GetLastMessageText(SummaryLangchain)

    # Now, generate a comparison JSON value.
    ComparisonLangchain: list = []
    ComparisonLangchain.append(
        Interface.BuildSystemQuery(SUMMARY_COMPARE_INTRO)
    )
    ComparisonLangchain.append(
        Interface.BuildUserQuery(
            SUMMARY_COMPARE_PROMPT.format(
                WorkSummary=WorkSummary, OutlineSummary=OutlineSummary
            )
        )
    )
    ComparisonLangchain = Interface.SafeGenerateText(
        _Logger, ComparisonLangchain, Writer.Config.REVISION_MODEL, _Format="json"
    )  # CHANGE THIS MODEL EVENTUALLY - BUT IT WORKS FOR NOW!!!

    Iters: int = 0
    while True:

        RawResponse = Interface.GetLastMessageText(ComparisonLangchain)
        RawResponse = RawResponse.replace("`", "")
        RawResponse = RawResponse.replace("json", "")

        try:
            Iters += 1
            Dict = json.loads(RawResponse)
            return (
                Dict["DidFollowOutline"],
                "### Extra Suggestions:\n" + Dict["Suggestions"],
            )
        except Exception as E:
            if Iters > 4:
                _Logger.Log("Critical Error Parsing JSON", 7)
                return False, ""

            _Logger.Log("Error Parsing JSON Written By LLM, Asking For Edits", 7)
            EditPrompt: str = (
                f"Please revise your JSON. It encountered the following error during parsing: {E}. Remember that your entire response is plugged directly into a JSON parser, so don't write **anything** except pure json."
            )
            ComparisonLangchain.append(Interface.BuildUserQuery(EditPrompt))
            _Logger.Log("Asking LLM TO Revise", 7)
            ComparisonLangchain = Interface.SafeGenerateText(
                _Logger,
                ComparisonLangchain,
                Writer.Config.REVISION_MODEL,
                _Format="json",
            )
            _Logger.Log("Done Asking LLM TO Revise JSON", 6)


class ChapterSummaryChecker:
    """
    章节摘要检查器类
    用于比较章节内容与大纲的一致性
    """
    
    def __init__(self, llm_editor):
        """
        初始化摘要检查器
        
        参数:
            llm_editor: LLM编辑器实例
        """
        self.llm = llm_editor
        
    def check_chapter(self, chapter, outline):
        """
        检查章节是否符合大纲
        
        参数:
            chapter (str): 章节内容
            outline (str): 大纲内容
            
        返回:
            dict: 检查结果
        """
        # 获取章节摘要
        chapter_summary = self._get_chapter_summary(chapter)
        
        # 获取大纲摘要
        outline_summary = self._get_outline_summary(outline)
        
        # 比较两个摘要
        return self._compare_summaries(chapter_summary, outline_summary)
        
    def _get_chapter_summary(self, chapter):
        """
        获取章节摘要
        
        参数:
            chapter (str): 章节内容
            
        返回:
            str: 章节摘要
        """
        prompt = SUMMARY_CHECK_PROMPT.format(_Work=chapter)
        return self.llm.generate(prompt)
        
    def _get_outline_summary(self, outline):
        """
        获取大纲摘要
        
        参数:
            outline (str): 大纲内容
            
        返回:
            str: 大纲摘要
        """
        prompt = SUMMARY_OUTLINE_PROMPT.format(_RefSummary=outline)
        return self.llm.generate(prompt)
        
    def _compare_summaries(self, chapter_summary, outline_summary):
        """
        比较章节摘要和大纲摘要
        
        参数:
            chapter_summary (str): 章节摘要
            outline_summary (str): 大纲摘要
            
        返回:
            dict: 比较结果
        """
        prompt = SUMMARY_COMPARE_PROMPT.format(
            WorkSummary=chapter_summary,
            OutlineSummary=outline_summary
        )
        response = self.llm.generate(prompt, format="json")
        return self.llm.parse_json_response(response)
