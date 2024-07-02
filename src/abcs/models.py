from pydantic import BaseModel


class UsageStats(BaseModel):
    input_tokens: int
    output_tokens: int
    extra: object

class PromptResponse(BaseModel):
    content: str
    raw_response: any
    error: object
    usage: UsageStats

class OllamaMessage(BaseModel):
    role: str
    content: str

class OllamaResponse(BaseModel):
    model: str
    created_at: str
    message: OllamaMessage
    done: bool
    total_duration: int
    load_duration: int
    prompt_eval_count: int
    prompt_eval_duration: int
    eval_count: int
    eval_duration: int
