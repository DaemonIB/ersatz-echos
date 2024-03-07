import argparse
import json
import logging
import uuid
from datetime import datetime
from random import randint, sample

import outlines
from outlines import models
from outlines.models.openai import OpenAIConfig
from pydantic import BaseModel, Field, ValidationError
import os
import PyPDF2
from context_creator import ContextItem

logger = logging.getLogger('ersatz_echos')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

# Read the configuration from a JSON file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

with open('user_context.json', 'r') as file:
    context = json.load(file)


class Event(BaseModel):
    year: int = Field(default=0,
                      gt=0,
                      description="The year the event starts",
                      examples=["0", "2050", "300", "8000", "70"])
    scale: str = Field(default="Period",
                       pattern=r'(?:Period|Middling|Scene)',
                       description="""
    Periods are the beginning of large events, middlings are specific occurrences within Periods that move the \
    narrative forward, and scenes are the most granular level, detailing specific moments within Events where \
    characters interact and specific outcomes are determined. Descriptions should take into \
    account the scale of the event being described.
    """)
    length: int = Field(default=1,
                        gt=0,
                        description="The length in years of the event",
                        examples=["0", "2050", "300", "8000", "70"])
    event: str = Field(default="",
                       description="The name of the event",
                       examples=["Eruption of Mount Hotenow",
                                 "Year of Blue Fire",
                                 "The Sundering",
                                 "The Herald",
                                 "Acquisitions Incorporated",
                                 "The Wild Beyond the Witchlight",
                                 "Journeys Through the Radiant Citadel"])
    description: str = Field(default="",
                             description="The description of the event")


def create_context_prompt():
    prompt = "\nSome additional context for this world can be found below:\n"
    for category, items in context.items():
        prompt += f"{category}:\n"
        for item in items:
            prompt += f"- {item['Name']}: {item['Description']}\n"
    return prompt


@outlines.prompt
def create_system_prompt(setting, create_context, model_schema):
    """You are a world history creation bot, you are creating fake history for a {{setting}} setting.

    The response should follow this JSON format {{model_schema | schema}}

    {{create_context}}
    """


def create_event_model(setting):
    system_prompt = create_system_prompt(setting, create_context_prompt(), Event)
    model = models.openai_compatible_api(model_name=config['model_name'], api_key=config['openai_api_key'],
                                         base_url=config['openai_api_base'],
                                         config=OpenAIConfig(temperature=config['temperature'],
                                                             response_format={"type": "json_object"}),
                                         system_prompt=system_prompt)
    return model


# Implement an automatic_palette function to generate themes
def automatic_palette():
    themes = ["revolution",
              "discovery",
              "conflict",
              "peace",
              "technology",
              "expansion",
              "innovation",
              "rebellion",
              "diplomacy",
              "catastrophe",
              "enlightenment",
              "migration",
              "invention",
              "decay",
              "mythology",
              "trade",
              "espionage",
              "cultural fusion",
              "revival",
              "ecology"]
    # Determine the number of themes to include: at least 1, at most 3
    num_include = randint(1, 3)
    include = sample(themes, num_include)

    # Determine the remaining themes that can be potentially excluded
    potential_exclude = list(set(themes) - set(include))

    # Determine the number of themes to exclude from the remaining themes: at least 0, at most 3 Note: The upper
    # limit for exclusion is dynamically set to the length of potential_exclude to avoid trying to exclude more
    # themes than available
    num_exclude = randint(0, min(3, len(potential_exclude)))

    # Randomly select themes to exclude, based on the number determined above
    exclude = sample(potential_exclude, num_exclude)

    return {"include": include, "exclude": exclude}


def generate_year(start_year, end_year):
    next_year = randint(start_year, end_year)
    return min(next_year, end_year)


# TODO: Move as much of this as possible into the system prompt to prevent it taking up memory
# Function to generate historical events using LangChain and OpenAI Chat API
def generate_event(start_year, num_events, end_year, llm_generates_year, history):
    # Prevents the LLM from getting stuck outputting the same results in a deterministic loop
    prompt = "" + str(uuid.uuid4()) + "\n"
    palette = automatic_palette()
    palette_prompt = f"Include these themes {palette['include']} and exclude these themes {palette['exclude']}\n"
    prompt += palette_prompt

    limit_prompt = f"there will be a total of {num_events} number of years generated, with year {start_year} being " \
                   f"the beginning of history"
    event_information_prompt = f"Events will be generated up to year {end_year}, {limit_prompt}\n"
    prompt += event_information_prompt

    # Include the current sorted history in the prompt
    history_prompt = "Current history:\n"
    for event in sorted(history, key=lambda x: x['year']):
        history_prompt += f"{event['year']}: {event['event']}\n"
    prompt += history_prompt

    # Generate the event description based on the event type
    if llm_generates_year:
        prompt += f"""Generate a historical event description including the year it occurred:"""
    else:
        year = generate_year(start_year, end_year)
        prompt += f"Generate a historical event description for the year {year}:"

    model = create_event_model(config['setting'])
    generator = outlines.generate.text(model)

    try_generate = True

    raw_event_response = ""
    event_response = Event()
    while try_generate:
        try:
            raw_event_response = generator(prompt)
            event_response: Event = Event.parse_raw(raw_event_response)
            try_generate = False
        except ValidationError:
            logger.debug("JSON formatting failure, trying again.")
            continue

    # Extract year from the response if LLM generates it
    year = event_response.year

    return year, raw_event_response


# Function to create the history JSON object
def create_history(start_year, end_year, num_events=10, llm_generates_year=True):
    history = []
    for i in range(num_events):
        current_year, event = generate_event(start_year, num_events, end_year, llm_generates_year, history)
        logger.info(event)
        history.append({
            "id": i + 1,
            "year": current_year,
            "event": event,
            "timestamp": datetime.utcnow().isoformat()
        })
    return history


# Function to save the history to a JSON file
def save_to_json(history, filename):
    # Sort the history list by the year of each event before saving
    sorted_history = sorted(history, key=lambda x: x['year'])
    with open(filename, 'w') as f:
        json.dump(sorted_history, f, indent=4)


@outlines.prompt
def create_extraction_system_prompt(model_schema):
    """You are a data extraction system, designed to extract and transform entities from pdfs into other formats.

    If no entities are detected, return nothing.

    The response should follow this JSON format {{model_schema | schema}}
    """


def create_extraction_model():
    system_prompt = create_extraction_system_prompt(ContextItem)
    model = models.openai_compatible_api(model_name=config['model_name'], api_key=config['openai_api_key'],
                                         base_url=config['openai_api_base'],
                                         config=OpenAIConfig(temperature=config['temperature'],
                                                             response_format={"type": "json_object"}),
                                         system_prompt=system_prompt)
    return model


def extract_information(text, category_name, model_schema):
    prompt = f"Extract entities that match the '{category_name}' from the following text:\n\n{text}"

    model = create_extraction_model()
    generator = outlines.generate.text(model)

    raw_response = generator(prompt)
    extracted_info = model_schema.parse_raw(raw_response)

    return extracted_info


def extract_information_from_pdfs(folder_path):
    for category, _ in context.items():
        context[category] = []

    # Iterate through each PDF in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)

            # Open the PDF file and read its text
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                pdf_text = ''
                for page in range(len(pdf_reader.pages)):
                    pdf_text += pdf_reader.pages[page].extract_text()

            # Iterate through the different context categories
            for category, _ in context.items():
                extracted_info = extract_information(pdf_text, category, ContextItem)
                context[category].append(extracted_info)


# Main function to run the application
def main():
    parser = argparse.ArgumentParser(description="Generate a fictional history timeline using AI.")
    parser.add_argument('--events', type=int, help='Number of events to generate')
    parser.add_argument('--output', type=str, help='Output JSON filename')

    args = parser.parse_args()

    # Use command line arguments if provided, otherwise use config file values
    events_count = args.events if args.events is not None else config['events_count']
    output_file = args.output if args.output is not None else config['output_file']
    start_year = config.get('start_year', 1000)
    end_year = config.get('end_year', 2000)
    llm_generates_year = config.get('llm_generates_year', True)

    print("Generating history...")
    history = create_history(start_year, end_year, events_count, llm_generates_year)
    save_to_json(history, output_file)
    print(f"History saved to {output_file}")


if __name__ == "__main__":
    document_extraction = config.get('document_extraction', False)
    if document_extraction:
        extract_information_from_pdfs('pdfs')

    main()
