from abcs.tool_models import (
    AnthropicTool,
    BaseTool,
    CohereTool,
    GoogleTool,
    OpenAIFunction,
    OpenAITool,
)


def gen_anthropic(tool):
    tool_def = BaseTool(**tool)
    deff = AnthropicTool(
        name=tool_def.name,
        description=tool_def.description,
        input_schema=tool_def.parameter_schema,
    )
    return deff.model_dump()



def gen_openai(tool):
    tool_def = BaseTool(**tool)
    deff = OpenAITool(
        type="function",
        function=OpenAIFunction(
            name=tool_def.name,
            description=tool_def.description,
            parameters=tool_def.parameter_schema,
        ),
    )
    return deff.model_dump()

def gen_cohere(tool):
    tool_def = BaseTool(**tool)
    parameter_definitions = {}
    # print(tool_def)
    # todo: needs to support all types, and be recursive, low-pri
    for prop_name in tool_def.parameter_schema['properties']:
        prop = tool_def.parameter_schema['properties'][prop_name]
        one_def = prop.copy()
        if one_def['type'] == 'string':
            one_def['type'] = 'str'
        parameter_definitions[prop_name] = one_def

    deff = CohereTool(
        name=tool_def.name,
        description=tool_def.description,
        parameter_definitions=parameter_definitions,
    )
    return deff.model_dump()

def gen_google(tool):
    tool_def = BaseTool(**tool)
    tool_copy = dict(tool_def.parameter_schema)
    if 'examples' in tool_copy:
        del tool_copy['examples']
    deff = GoogleTool(
        name=tool_def.name,
        description=tool_def.description,
        parameters=tool_copy,
    )

    return deff.model_dump()
