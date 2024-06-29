import Writer.PrintUtils

import json


def GetFeedbackOnOutline(Interface, _Logger, _Outline: str):

    # Setup Initial Context History
    History = []
    History.append(Interface.BuildSystemQuery(f"You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."))


    StartingPrompt: str = f"""
Please critique the following outline - make sure to provide constructive criticism on how it can be improved and point out any problems with it.

<OUTLINE>
{_Outline}
</OUTLINE>

As you revise, consider the following criteria:
    - Pacing: Is the story rushing over certain plot points and excessively focusing on others?
    - Details: How are things described? Is it repetitive? Is the word choice appropriate for the scene? Are we describing things too much or too little?
    - Flow: Does each chapter flow into the next? Does the plot make logical sense to the reader? Does it have a specific narrative structure at play? Is the narrative structure consistent throughout the story?
    - Genre: What is the genre? What language is appropriate for that genre? Do the scenes support the genre?

Also, please check if the outline is written chapter-by-chapter, not in sections spanning multiple chapters or subsections.
It should be very clear which chapter is which, and the content in each chapter.

    """

    _Logger.Log("Prompting LLM To Critique Outline", 5)
    History.append(Interface.BuildUserQuery(StartingPrompt))
    History = Interface.ChatAndStreamResponse(
        _Logger, History, Writer.Config.REVISION_MODEL
    )
    _Logger.Log("Finished Getting Outline Feedback", 5)

    return Interface.GetLastMessageText(History)


def GetOutlineRating(Interface, _Logger, _Outline: str,):

    # Setup Initial Context History
    History = []
    History.append(Interface.BuildSystemQuery(f"You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."))



    StartingPrompt: str = f"""

<OUTLINE>
{_Outline}
</OUTLINE>

This outline meets all of the following criteria (true or false):
    - Pacing: Is the story rushing over certain plot points and excessively focusing on others?
    - Details: How are things described? Is it repetitive? Is the word choice appropriate for the scene? Are we describing things too much or too little?
    - Flow: Does each chapter flow into the next? Does the plot make logical sense to the reader? Does it have a specific narrative structure at play? Is the narrative structure consistent throughout the story?
    - Genre: What is the genre? What language is appropriate for that genre? Do the scenes support the genre?

Give a JSON formatted response, containing the string \"IsComplete\", followed by an boolean True/False.
Please do not include any other text, just the JSON as your response will be parsed by a computer.
"""

    _Logger.Log("Prompting LLM To Get Review JSON", 5)

    History.append(Interface.BuildUserQuery(StartingPrompt))
    History = Interface.ChatAndStreamResponse(
        _Logger, Messages, Writer.Config.EVAL_MODEL, _Format="json"
    )
    _Logger.Log("Finished Getting Review JSON", 5)

    Iters: int = 0
    while True:

        RawResponse = Interface.GetLastMessageText(History)
        RawResponse = RawResponse.replace("`", "")
        RawResponse = RawResponse.replace("json", "")

        try:
            Iters += 1
            Rating = json.loads(RawResponse)["IsComplete"]
            _Logger.Log(f"Editor Determined IsComplete: {Rating}", 5)
            return Rating
        except Exception as E:
            if Iters > 4:
                _Logger.Log("Critical Error Parsing JSON", 7)
                return False
            _Logger.Log("Error Parsing JSON Written By LLM, Asking For Edits", 7)
            EditPrompt: str = (
                f"Please revise your JSON. It encountered the following error during parsing: {E}. Remember that your entire response is plugged directly into a JSON parser, so don't write **anything** except pure json."
            )
            History.append(Interface.BuildUserQuery(EditPrompt))
            _Logger.Log("Asking LLM TO Revise", 7)
            History = Interface.ChatAndStreamResponse(
                _Logger, History, Writer.Config.EVAL_MODEL, _Format="json

            )
            _Logger.Log("Done Asking LLM TO Revise JSON", 6)


def GetFeedbackOnChapter(Interface, _Logger, _Chapter: str, _Outline: str):

    # Setup Initial Context History
    History = []
    History.append(Interface.BuildSystemQuery(f"You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."))


    # Disabled seeing the outline too.
    StartingPrompt: str = f"""
<CHAPTER>
{_Chapter}
</CHAPTER>

Please give feedback on the above chapter based on the following criteria:
    - Pacing: Is the story rushing over certain plot points and excessively focusing on others?
    - Details: How are things described? Is it repetitive? Is the word choice appropriate for the scene? Are we describing things too much or too little?
    - Flow: Does each chapter flow into the next? Does the plot make logical sense to the reader? Does it have a specific narrative structure at play? Is the narrative structure consistent throughout the story?
    - Genre: What is the genre? What language is appropriate for that genre? Do the scenes support the genre?
    
    - Characters: Who are the characters in this chapter? What do they mean to each other? What is the situation between them? Is it a conflict? Is there tension? Is there a reason that the characters have been brought together?
    - Development:  What are the goals of each character, and do they meet those goals? Do the characters change and exhibit growth? Do the goals of each character change over the story?
    
    - Dialogue: Does the dialogue make sense? Is it appropriate given the situation? Does the pacing make sense for the scene E.g: (Is it fast-paced because they're running, or slow-paced because they're having a romantic dinner)? 
    - Disruptions: If the flow of dialogue is disrupted, what is the reason for that disruption? Is it a sense of urgency? What is causing the disruption? How does it affect the dialogue moving forwards? 

"""

    _Logger.Log("Prompting LLM To Critique Chapter", 5)
    History.append(Interface.BuildUserQuery(StartingPrompt))
    Messages = Interface.ChatAndStreamResponse(_Logger, History, Writer.Config.REVISION_MODEL)
    _Logger.Log("Finished Getting Chapter Feedback", 5)

    return Interface.GetLastMessageText(Messages)


# Switch this to iscomplete true/false (similar to outline)
def GetChapterRating(Interface, _Logger, _Chapter: str):

    # Setup Initial Context History
    History = []
    History.append(Interface.BuildSystemQuery(f"You are a helpful AI Assistant. Answer the user's prompts to the best of your abilities."))


    StartingPrompt: str = f"""

<CHAPTER>
{_Chapter}
</CHAPTER>

This chapter meets all of the following criteria (true or false):
    - Pacing: Is the story rushing over certain plot points and excessively focusing on others?
    - Details: How are things described? Is it repetitive? Is the word choice appropriate for the scene? Are we describing things too much or too little?
    - Flow: Does each chapter flow into the next? Does the plot make logical sense to the reader? Does it have a specific narrative structure at play? Is the narrative structure consistent throughout the story?
    - Genre: What is the genre? What language is appropriate for that genre? Do the scenes support the genre?

Give a JSON formatted response, containing the string \"IsComplete\", followed by an boolean True/False.
Please do not include any other text, just the JSON as your response will be parsed by a computer.
"""

    _Logger.Log("Prompting LLM To Get Review JSON", 5)
    History.append(Interface.BuildUserQuery(StartingPrompt))
    History = Interface.ChatAndStreamResponse(_Logger, History, Writer.Config.EVAL_MODEL)
    _Logger.Log("Finished Getting Review JSON", 5)

    Iters: int = 0
    while True:

        RawResponse = Interface.GetLastMessageText(History)
        RawResponse = RawResponse.replace("`", "")
        RawResponse = RawResponse.replace("json", "")

        try:
            Iters += 1
            Rating = json.loads(RawResponse)["IsComplete"]
            _Logger.Log(f"Editor Determined IsComplete: {Rating}", 5)
            return Rating
        except Exception as E:
            if Iters > 4:
                _Logger.Log("Critical Error Parsing JSON", 7)
                return False

            _Logger.Log("Error Parsing JSON Written By LLM, Asking For Edits", 7)
            EditPrompt: str = (f"Please revise your JSON. It encountered the following error during parsing: {E}. Remember that your entire response is plugged directly into a JSON parser, so don't write **anything** except pure json.")
            History.append(Interface.BuildUserQuery(EditPrompt))
            _Logger.Log("Asking LLM TO Revise", 7)
            History = Interface.ChatAndStreamResponse(_Logger, History, Writer.Config.EVAL_MODEL)
            _Logger.Log("Done Asking LLM TO Revise JSON", 6)
