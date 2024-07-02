from pydantic import BaseModel


class BaseTool(BaseModel):
    name: str
    description: str
    parameter_schema: object


class AnthropicTool(BaseModel):
    name: str
    description: str
    input_schema: object


class CohereTool(BaseModel):
    name: str
    description: str
    parameter_definitions: object


class GoogleTool(BaseModel):
    name: str
    description: str
    parameters: object

class OpenAIFunction(BaseModel):
    name: str
    description: str
    parameters: object


class OpenAITool(BaseModel):
    type: str
    function: OpenAIFunction
