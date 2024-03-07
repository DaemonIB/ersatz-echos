import argparse
import json
import logging
import re
from datetime import datetime
from random import randint, sample

from langchain.memory import ChatMessageHistory
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

logging.getLogger().setLevel(logging.INFO)

# Read the configuration from a JSON file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

with open('user_context.json', 'r') as file:
    context = json.load(file)


def create_context_prompt():
    prompt = "\nSome additional context for this world can be found below:\n"
    for category, items in context.items():
        prompt += f"{category}:\n"
        for item in items:
            prompt += f"- {item['Name']}: {item['Description']}\n"
    return prompt


system_template = (
        """You are a world history creation bot, you are creating fake history for a {setting} setting.\n Your 
        response should be in the following format Year: <year> Scale: <scale> Length: <length_in_years> Event: 
        <event_name> Description: <event_description>\n Generate events at all scales which include periods, 
        middlings, and scenes. Periods are the beginning of large events, middlings are specific occurrences within 
        Periods that move the narrative forward, and scenes are the most granular level, detailing specific moments 
        within Events where characters interact and specific outcomes are determined. Descriptions should take into 
        account the scale of the event being described.\n"""
        + create_context_prompt()
)
system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

human_template = "{text}"
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

chat_prompt = ChatPromptTemplate.from_messages(
    [system_message_prompt,
     MessagesPlaceholder(variable_name="chat_history"),
     human_message_prompt]
)

ephemeral_chat_history = ChatMessageHistory()

chat = ChatOpenAI(temperature=config['temperature'],
                  openai_api_key=config['openai_api_key'],
                  openai_api_base=config['openai_api_base'],
                  model_name=config['model_name'])

chain = chat_prompt | chat

chain_with_message_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: ephemeral_chat_history,
    input_messages_key="text",
    history_messages_key="chat_history",
)


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
def generate_event(start_year, num_events, end_year, llm_generates_year):
    prompt = ""
    palette = automatic_palette()
    palette_prompt = f"Include these themes {palette['include']} and exclude these themes {palette['exclude']}\n"
    prompt += palette_prompt

    limit_prompt = f"there will be a total of {num_events} number of years generated, with year {start_year} being " \
                   f"the beginning of history"
    event_information_prompt = f"Events will be generated up to year {end_year}, {limit_prompt}\n"
    prompt += event_information_prompt

    year = "Unknown"

    # Generate the event description based on the event type
    if llm_generates_year:
        prompt += f"""Generate a historical event description including the year it occurred:"""
    else:
        year = generate_year(start_year, end_year)
        prompt += f"Generate a historical event description for the year {year}:"

    response = chain_with_message_history.invoke(
        {"setting": config['setting'], "text": prompt},
        {"configurable": {"session_id": "unused"}},
    )

    # Extract year from the response if LLM generates it
    if llm_generates_year:
        response_text = response.content
        year_match = re.search(r'Year: (\d+)', response_text)
        if year_match:
            year = int(year_match.group(1))
        else:
            logging.warning("Year not found in LLM response. Using current year.")

    return year, response


# Function to create the history JSON object
def create_history(start_year, end_year, num_events=10, llm_generates_year=True):
    history = []
    for i in range(num_events):
        current_year, event = generate_event(start_year, num_events, end_year, llm_generates_year)
        logging.info(event)
        history.append({
            "id": i + 1,
            "year": current_year,
            "event": event.content,
            "timestamp": datetime.utcnow().isoformat()
        })
    return history


# Function to save the history to a JSON file
def save_to_json(history, filename):
    # Sort the history list by the year of each event before saving
    sorted_history = sorted(history, key=lambda x: x['year'])
    with open(filename, 'w') as f:
        json.dump(sorted_history, f, indent=4)


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
    main()
