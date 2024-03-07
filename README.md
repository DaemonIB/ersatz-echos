# Ersatz Echos

Ersatz Echos is an AI-powered history generator that creates rich, structured timelines for fictional worlds. With customizable parameters and the ability to draw inspiration from user-provided documents, Ersatz Echos crafts unique histories spanning centuries or millennia. The tool outputs its generated histories in a structured JSON format, making it easy to integrate with other world-building applications. Whether you're a game developer, novelist, or simply a creative enthusiast, Ersatz Echos provides a foundation for building immersive, consistent fictional universes.

## Features

- AI-driven history generation using advanced language models
- Customizable timeline parameters (start year, end year, number of events, etc..)
- Structured JSON output for easy integration with other tools
- Experimental features for enhanced world-building capabilities
  - Ability to extract information from user-provided PDF documents for added context

## Getting Started

### Prerequisites

- Access to an API (OpenAI, OpenRouter, etc.)
- Python 3.11+ installed

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/DaemonIB/ersatz-echos.git
   ```

2. Navigate to the project directory:
   ```
   cd ersatz-echos
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Copy the example configuration files:
   ```
   cp user_context.example.json user_context.json
   cp config.example.json config.json
   ```

5. Edit `config.json` and replace `YOUR_API_KEY_HERE` with your LLM API key.

6. (Optional) If you want to provide additional context for the LLM to base the timeline on:
   - Edit `user_context.json` and replace the sample data with your own data.

### Usage

Run the Python script:
```
python main.py --output history.json
```

The generated history will be saved to the file specified with the `--output` flag, or `history.json` if not specified.

## Configuration

- `config.json`: Contains settings for the LLM API and other parameters.
- `user_context.json`: Allows you to provide additional context for the LLM to base the timeline on. The structure is generic, and any top-level category can be used (e.g., `Locations`, `Characters`, `Funny Hair Styles`). Individual entities within each category need a `name` and `description`.

## Notes

- The default model has been selected based on cost and ability to produce JSON. For OpenAI, `openai/gpt-3.5-turbo-0125` is compatible, along with the models specified [here](https://platform.openai.com/docs/api-reference/chat/create#chat-create-response_format).
- Other models may work, but their success rate may be lower.

## Experimental Features

- Document Extraction: Enabled via the `document_extraction` flag in `config.json`.

## License

This project is licensed under [Apache-2.0](LICENSE).