"""
接口包装器模块
用于封装和统一管理不同LLM接口的访问
"""

import Writer.Config
import dotenv
import inspect
import json
import os
import time
import random
import importlib
import subprocess
import sys
from urllib.parse import parse_qs, urlparse

dotenv.load_dotenv()


class Interface:
    """
    接口类
    提供统一的接口来访问不同的LLM服务
    """

    def __init__(
        self,
        Models: list = [],
    ):
        """
        初始化接口
        
        参数:
            Models (list): 要加载的模型列表
        """
        self.Clients: dict = {}
        self.History = []
        self.LoadModels(Models)

    def ensure_package_is_installed(self, package_name):
        """
        确保所需的Python包已安装
        
        参数:
            package_name (str): 包名
        """
        try:
            importlib.import_module(package_name)
        except ImportError:
            print(f"未找到{package_name}包，正在安装...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package_name]
            )

    def LoadModels(self, Models: list):
        """
        加载模型
        
        参数:
            Models (list): 要加载的模型列表
        """
        for Model in Models:
            if Model in self.Clients:
                continue
            else:
                Provider, ProviderModel, ModelHost, ModelOptions = (
                    self.GetModelAndProvider(Model)
                )
                print(f"调试: 正在从{Provider}@{ModelHost}加载模型{ProviderModel}")

                if Provider == "ollama":
                    # 获取ollama模型(仅一次)
                    self.ensure_package_is_installed("ollama")
                    import ollama

                    OllamaHost = ModelHost if ModelHost is not None else None

                    # 检查模型是否可用
                    try:
                        ollama.Client(host=OllamaHost).show(ProviderModel)
                        pass
                    except Exception as e:
                        print(
                            f"在Ollama模型中未找到{ProviderModel}，正在下载..."
                        )
                        OllamaDownloadStream = ollama.Client(host=OllamaHost).pull(
                            ProviderModel, stream=True
                        )
                        for chunk in OllamaDownloadStream:
                            if "completed" in chunk and "total" in chunk:
                                OllamaDownloadProgress = (
                                    chunk["completed"] / chunk["total"]
                                )
                                completedSize = chunk["completed"] / 1024**3
                                totalSize = chunk["total"] / 1024**3
                                print(
                                    f"正在下载{ProviderModel}: {OllamaDownloadProgress * 100:.2f}% ({completedSize:.3f}GB/{totalSize:.3f}GB)",
                                    end="\r",
                                )
                            else:
                                print(f"{chunk['status']} {ProviderModel}", end="\r")
                        print("\n\n\n")

                    self.Clients[Model] = ollama.Client(host=OllamaHost)
                    print(f"OLLAMA主机为'{OllamaHost}'")

                elif Provider == "google":
                    # 验证Google API密钥
                    if (
                        not "GOOGLE_API_KEY" in os.environ
                        or os.environ["GOOGLE_API_KEY"] == ""
                    ):
                        raise Exception(
                            "环境变量中未找到GOOGLE_API_KEY"
                        )
                    self.ensure_package_is_installed("google-generativeai")
                    import google.generativeai as genai

                    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
                    self.Clients[Model] = genai.GenerativeModel(
                        model_name=ProviderModel
                    )

                elif Provider == "openai":
                    raise NotImplementedError("不支持OpenAI API")

                elif Provider == "openrouter":
                    if (
                        not "OPENROUTER_API_KEY" in os.environ
                        or os.environ["OPENROUTER_API_KEY"] == ""
                    ):
                        raise Exception(
                            "环境变量中未找到OPENROUTER_API_KEY"
                        )
                    from Writer.Interface.OpenRouter import OpenRouter

                    self.Clients[Model] = OpenRouter(
                        api_key=os.environ["OPENROUTER_API_KEY"], model=ProviderModel
                    )

                elif Provider == "Anthropic":
                    raise NotImplementedError("不支持Anthropic API")

                else:
                    print(f"警告, ")
                    raise Exception(f"未找到{Model}的模型提供者{Provider}")

    def SafeGenerateText(
        self,
        _Logger,
        _Messages,
        _Model: str,
        _SeedOverride: int = -1,
        _Format: str = None,
        _MinWordCount: int = 1
        ):
        """
        安全地生成文本，确保输出不为空
        
        参数:
            _Logger: 日志记录器
            _Messages: 消息历史
            _Model: 模型名称
            _SeedOverride: 随机种子覆盖值
            _Format: 期望的输出格式
            _MinWordCount: 最小字数要求
        """
        # 删除空消息
        for i in range(len(_Messages) - 1, 0, -1):
            if _Messages[i]["content"].strip() == "":
                del _Messages[i]

        NewMsg = self.ChatAndStreamResponse(_Logger, _Messages, _Model, _SeedOverride, _Format)

        while (self.GetLastMessageText(NewMsg).strip() == "") or (len(self.GetLastMessageText(NewMsg).split(" ")) < _MinWordCount):
            if self.GetLastMessageText(NewMsg).strip() == "":
                _Logger.Log("SafeGenerateText: 生成失败，响应为空(空白)，正在重试", 7)
            elif (len(self.GetLastMessageText(NewMsg).split(" ")) < _MinWordCount):
                _Logger.Log(f"SafeGenerateText: 生成失败，响应过短({len(self.GetLastMessageText(NewMsg).split(' '))}，最小要求{_MinWordCount})，正在重试", 7)

            del _Messages[-1] # 删除失败的尝试
            NewMsg = self.ChatAndStreamResponse(_Logger, _Messages, _Model, random.randint(0, 99999), _Format)

        return NewMsg



    def SafeGenerateJSON(self, _Logger, _Messages, _Model:str, _SeedOverride:int = -1, _RequiredAttribs:list = []):

        while True:
            Response = self.SafeGenerateText(_Logger, _Messages, _Model, _SeedOverride, _Format = "JSON")
            try:

                # Check that it returned valid json
                JSONResponse = json.loads(self.GetLastMessageText(Response))

                # Now ensure it has the right attributes
                for _Attrib in _RequiredAttribs:
                    JSONResponse[_Attrib]

                # Now return the json
                return Response, JSONResponse

            except Exception as e:
                _Logger.Log(f"JSON Error during parsing: {e}", 7)
                del _Messages[-1] # Remove failed attempt
                Response = self.ChatAndStreamResponse(_Logger, _Messages, _Model, random.randint(0, 99999), _Format = "JSON")



    def ChatAndStreamResponse(
        self,
        _Logger,
        _Messages,
        _Model: str = "llama3",
        _SeedOverride: int = -1,
        _Format: str = None,
    ):
        Provider, ProviderModel, ModelHost, ModelOptions = self.GetModelAndProvider(
            _Model
        )

        # Calculate Seed Information
        Seed = Writer.Config.SEED if _SeedOverride == -1 else _SeedOverride

        # Log message history if DEBUG is enabled
        if Writer.Config.DEBUG:
            print("--------- Message History START ---------")
            print("[")
            for Message in _Messages:
                print(f"{Message},\n----\n")
            print("]")
            print("--------- Message History END --------")

        StartGeneration = time.time()

        # Calculate estimated tokens
        TotalChars = len(str(_Messages))
        AvgCharsPerToken = 5  # estimated average chars per token
        EstimatedTokens = TotalChars / AvgCharsPerToken
        _Logger.Log(
            f"Using Model '{ProviderModel}' from '{Provider}@{ModelHost}' | (Est. ~{EstimatedTokens}tok Context Length)",
            4,
        )

        # Log if there's a large estimated tokens of context history
        if EstimatedTokens > 24000:
            _Logger.Log(
                f"Warning, Detected High Token Context Length of est. ~{EstimatedTokens}tok",
                6,
            )

        if Provider == "ollama":

            # remove host
            if "@" in ProviderModel:
                ProviderModel = ProviderModel.split("@")[0]

            # https://github.com/ollama/ollama/blob/main/docs/modelfile.md#valid-parameters-and-values
            ValidParameters = [
                "mirostat",
                "mirostat_eta",
                "mirostat_tau",
                "num_ctx",
                "repeat_last_n",
                "repeat_penalty",
                "temperature",
                "seed",
                "tfs_z",
                "num_predict",
                "top_k",
                "top_p",
            ]
            ModelOptions = ModelOptions if ModelOptions is not None else {}

            # Check if the parameters are valid
            for key in ModelOptions:
                if key not in ValidParameters:
                    raise ValueError(f"Invalid parameter: {key}")

            # Set the default num_ctx if not set by args
            if "num_ctx" not in ModelOptions:
                ModelOptions["num_ctx"] = Writer.Config.OLLAMA_CTX

            _Logger.Log(f"Using Ollama Model Options: {ModelOptions}", 4)

            if _Format == "json":
                # Overwrite the format to JSON
                ModelOptions["format"] = "json"

                # if temperature is not set, set it to 0 for JSON mode
                if "temperature" not in ModelOptions:
                    ModelOptions["temperature"] = 0
                _Logger.Log("Using Ollama JSON Format", 4)

            Stream = self.Clients[_Model].chat(
                model=ProviderModel,
                messages=_Messages,
                stream=True,
                options=ModelOptions,
            )
            MaxRetries = 3

            while True:
                try:
                    _Messages.append(self.StreamResponse(Stream, Provider))
                    break
                except Exception as e:
                    if MaxRetries > 0:
                        _Logger.Log(
                            f"Exception During Generation '{e}', {MaxRetries} Retries Remaining",
                            7,
                        )
                        MaxRetries -= 1
                    else:
                        _Logger.Log(
                            f"Max Retries Exceeded During Generation, Aborting!", 7
                        )
                        raise Exception(
                            "Generation Failed, Max Retires Exceeded, Aborting"
                        )

        elif Provider == "google":

            from google.generativeai.types import (
                HarmCategory,
                HarmBlockThreshold,
            )

            # replace "content" with "parts" for google
            _Messages = [{"role": m["role"], "parts": m["content"]} for m in _Messages]
            for m in _Messages:
                if "content" in m:
                    m["parts"] = m["content"]
                    del m["content"]
                if "role" in m and m["role"] == "assistant":
                    m["role"] = "model"
                    # Google doesn't support "system" role while generating content (only while instantiating the model)
                if "role" in m and m["role"] == "system":
                    m["role"] = "user"

            MaxRetries = 3
            while True:
                try:
                    Stream = self.Clients[_Model].generate_content(
                        contents=_Messages,
                        stream=True,
                        safety_settings={
                            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        },
                    )
                    _Messages.append(self.StreamResponse(Stream, Provider))
                    break
                except Exception as e:
                    if MaxRetries > 0:
                        _Logger.Log(
                            f"Exception During Generation '{e}', {MaxRetries} Retries Remaining",
                            7,
                        )
                        MaxRetries -= 1
                    else:
                        _Logger.Log(
                            f"Max Retries Exceeded During Generation, Aborting!", 7
                        )
                        raise Exception(
                            "Generation Failed, Max Retires Exceeded, Aborting"
                        )

            # Replace "parts" back to "content" for generalization
            # and replace "model" with "assistant"
            for m in _Messages:
                if "parts" in m:
                    m["content"] = m["parts"]
                    del m["parts"]
                if "role" in m and m["role"] == "model":
                    m["role"] = "assistant"

        elif Provider == "openai":
            raise NotImplementedError("OpenAI API not supported")

        elif Provider == "openrouter":

            # https://openrouter.ai/docs/parameters
            # Be aware that parameters depend on models and providers.
            ValidParameters = [
                "max_token",
                "presence_penalty",
                "frequency_penalty",
                "repetition_penalty",
                "response_format",
                "temperature",
                "seed",
                "top_k",
                "top_p",
                "top_a",
                "min_p",
            ]
            ModelOptions = ModelOptions if ModelOptions is not None else {}

            Client = self.Clients[_Model]
            Client.set_params(**ModelOptions)
            Client.model = ProviderModel
            print(ProviderModel)

            Response = Client.chat(messages=_Messages, seed=Seed)
            _Messages.append({"role": "assistant", "content": Response})

        elif Provider == "Anthropic":
            raise NotImplementedError("Anthropic API not supported")

        else:
            raise Exception(f"Model Provider {Provider} for {_Model} not found")

        # Log the time taken to generate the response
        EndGeneration = time.time()
        _Logger.Log(
            f"Generated Response in {round(EndGeneration - StartGeneration, 2)}s (~{round(EstimatedTokens / (EndGeneration - StartGeneration), 2)}tok/s)",
            4,
        )
        # Check if the response is empty and attempt regeneration if necessary
        if _Messages[-1]["content"].strip() == "":
            _Logger.Log("Model Returned Only Whitespace, Attempting Regeneration", 6)
            _Messages.append(
                self.BuildUserQuery(
                    "Sorry, but you returned an empty string, please try again!"
                )
            )
            return self.ChatAndStreamResponse(_Logger, _Messages, _Model, _SeedOverride)

        CallStack: str = ""
        for Frame in inspect.stack()[1:]:
            CallStack += f"{Frame.function}."
        CallStack = CallStack[:-1].replace("<module>", "Main")
        _Logger.SaveLangchain(CallStack, _Messages)
        return _Messages

    def StreamResponse(self, _Stream, _Provider: str):
        Response: str = ""
        for chunk in _Stream:
            if _Provider == "ollama":
                ChunkText = chunk["message"]["content"]
            elif _Provider == "google":
                ChunkText = chunk.text
            else:
                raise ValueError(f"Unsupported provider: {_Provider}")

            Response += ChunkText
            print(ChunkText, end="", flush=True)

        print("\n\n\n" if Writer.Config.DEBUG else "")
        return {"role": "assistant", "content": Response}

    def BuildUserQuery(self, _Query: str):
        return {"role": "user", "content": _Query}

    def BuildSystemQuery(self, _Query: str):
        return {"role": "system", "content": _Query}

    def BuildAssistantQuery(self, _Query: str):
        return {"role": "assistant", "content": _Query}

    def GetLastMessageText(self, _Messages: list):
        return _Messages[-1]["content"]

    def GetModelAndProvider(self, _Model: str):
        # Format is `Provider://Model@Host?param1=value2&param2=value2`
        # default to ollama if no provider is specified
        if "://" in _Model:
            # this should be a valid URL
            parsed = urlparse(_Model)
            print(parsed)
            Provider = parsed.scheme

            if "@" in parsed.netloc:
                Model, Host = parsed.netloc.split("@")

            elif Provider == "openrouter":
                Model = f"{parsed.netloc}{parsed.path}"
                Host = None

            elif "ollama" in _Model:
                if "@" in parsed.path:
                    Model = parsed.netloc + parsed.path.split("@")[0]
                    Host = parsed.path.split("@")[1]
                else:
                    Model = parsed.netloc
                    Host = "localhost:11434"

            else:
                Model = parsed.netloc
                Host = None
            QueryParams = parse_qs(parsed.query)

            # Flatten QueryParams
            for key in QueryParams:
                QueryParams[key] = float(QueryParams[key][0])

            return Provider, Model, Host, QueryParams
        else:
            # legacy support for `Model` format
            return "ollama", _Model, "localhost:11434", None
