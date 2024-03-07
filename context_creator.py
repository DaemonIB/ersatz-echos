import json

import outlines
from outlines import models
from outlines.models.openai import OpenAIConfig
from pydantic import BaseModel, Field


class ContextItem(BaseModel):
    name: str = Field(description="The proper name of the entity",
                      examples=["Sir John Edwards", "London", "Canada", "The organization of shadows", "Monarchy"])
    description: str = Field(description="A description of the entity",
                             examples=["King of Evermore, a benevolent ruler with a mysterious past.",
                                       "Oversees ancient laws and magic within the Dark Forest.",
                                       "Control trade and commerce within the kingdom.",
                                       "A lost language believed to hold key to untold magic and history."])


# Read the configuration from a JSON file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

with open('user_context.json', 'r') as file:
    context = json.load(file)


def create_new_context(context_items, context_category, full_history):
    prompt = f"Generated history\n{full_history}"
    prompt += f"{context_category}:\nExamples:\n"
    for item in context_items:
        prompt += f"- {item['Name']}: {item['Description']}\n"
    return prompt


@outlines.prompt
def create_system_prompt(setting, create_context, model_schema):
    """You are a world history creation bot, you are creating fake history for a {{setting}} setting.

    The response should follow this JSON format {{model_schema | schema}}

    {{create_context}}
    """


def create_context_model(setting, context_items, context_category, full_history):
    system_prompt = create_system_prompt(setting, create_new_context(context_items, context_category, full_history),
                                         ContextItem)
    model = models.openai_compatible_api(model_name=config['model_name'], api_key=config['openai_api_key'],
                                         base_url=config['openai_api_base'],
                                         config=OpenAIConfig(temperature=config['temperature'],
                                                             response_format={"type": "json_object"}),
                                         system_prompt=system_prompt)
    return model


# Function to create the context JSON object
def generate_new_context(full_history):
    contexts = []
    prompt = f"\nGenerate a new item in this category\n"
    for category, items in context.items():
        model = create_context_model(config['setting'], items, category, full_history)
        generator = outlines.generate.text(model)
        new_context = generator(prompt)
        contexts.append(new_context)
    return contexts
