import os
import sys
from typing import Iterator, List, Optional, TypedDict, cast

try:
    from llama_cpp import Completion, CompletionChunk, Llama

    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False

from gptcli.completion import CompletionProvider, Message


class LLaMAModelConfig(TypedDict):
    path: str
    human_prompt: str
    assistant_prompt: str


# Global variable to store model configurations
LLAMA_MODELS = {}

def init_llama_models(model_path):
    global LLAMA_MODELS
    
    # Check if the model path exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"The model path {model_path} does not exist.")
    
    print(f"Initializing LLaMA models from path: {model_path}")
    
    # Initialize models as a dictionary with the correct model name
    models = {
        "llama-3.1-8b-instruct": model_path
    }
    
    # Load models into the global dictionary
    for name, model_config in models.items():
        # Assuming model_config is a path to the model file or directory
        LLAMA_MODELS[name] = model_config
        print(f"Initialized model {name} with config: {model_config}")

    print(f"LLaMA models initialized: {LLAMA_MODELS}")

# Ensure this script is executed
if __name__ == "__main__":
    init_llama_models("/Users/rescreen/.cache/lm-studio/models/lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q8_0.gguf")
    

def role_to_name(role: str, model_config: LLaMAModelConfig) -> str:
    if role == "system" or role == "user":
        return model_config["human_prompt"]
    elif role == "assistant":
        return model_config["assistant_prompt"]
    else:
        raise ValueError(f"Unknown role: {role}")


def make_prompt(messages: List[Message], model_config: LLaMAModelConfig) -> str:
    prompt = "\n".join(
        [
            f"{role_to_name(message['role'], model_config)} {message['content']}"
            for message in messages
        ]
    )
    prompt += f"\n{model_config['assistant_prompt']}"
    return prompt


class LLaMACompletionProvider(CompletionProvider):
    def complete(
        self, messages: List[Message], args: dict, stream: bool = False
    ) -> Iterator[str]:
        assert LLAMA_MODELS, "LLaMA models not initialized"

        model_config = LLAMA_MODELS[args["model"]]

        with suppress_stderr():
            llm = Llama(
                model_path=model_config["path"],
                n_ctx=2048,
                verbose=False,
                use_mlock=True,
            )
        prompt = make_prompt(messages, model_config)
        print(prompt)

        extra_args = {}
        if "temperature" in args:
            extra_args["temperature"] = args["temperature"]
        if "top_p" in args:
            extra_args["top_p"] = args["top_p"]

        gen = llm.create_completion(
            prompt,
            max_tokens=1024,
            stop=model_config["human_prompt"],
            stream=stream,
            echo=False,
            **extra_args,
        )
        if stream:
            for x in cast(Iterator[CompletionChunk], gen):
                yield x["choices"][0]["text"]
        else:
            yield cast(Completion, gen)["choices"][0]["text"]


# https://stackoverflow.com/a/50438156
class suppress_stderr(object):
    def __enter__(self):
        self.errnull_file = open(os.devnull, "w")
        self.old_stderr_fileno_undup = sys.stderr.fileno()
        self.old_stderr_fileno = os.dup(sys.stderr.fileno())
        self.old_stderr = sys.stderr
        os.dup2(self.errnull_file.fileno(), self.old_stderr_fileno_undup)
        sys.stderr = self.errnull_file
        return self

    def __exit__(self, *_):
        sys.stderr = self.old_stderr
        os.dup2(self.old_stderr_fileno, self.old_stderr_fileno_undup)
        os.close(self.old_stderr_fileno)
        self.errnull_file.close()
