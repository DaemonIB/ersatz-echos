# Ersatz Echos

## Running

### Pre-requisites
You will need access to an API, whether that be OpenAI, OpenRouter, etc...
Clone or download the repo
Copy `user_context.example.json` to `user_context.json`
Copy `config.example.json` to `config.json`
If you want to provide some information to the LLM to base its timeline off of do the following:
1. Copy `user_context.example.json` to `user_context.json`
2. Edit `user_context.json` as needed and replace the sample data with your own data
Edit `config.json` replace `YOUR_API_KEY_HERE` with your LLM API key

### Run
Windows
* Run `ersatz_echos.exe`

Linux/Mac
* Run ```python main.py --events 10 --output history.json```

After running a file matching the name passed to `--output` will be generated or `history.json` if none is specified.

## Compiling
Run ```compile.bat```
This will create an `.exe` file in the `dist` folder and copy it to the working directory.

## Notes
* Model selection
  * The default model has been selected based on cost/ability to produce json. For OpenAI `openai/gpt-3.5-turbo-0125` 
    is compatible along with the models specified here: https://platform.openai.com/docs/api-reference/chat/create#chat-create-response_format
  * Other models will likely still work, but their success rate may be lower, so your mileage may vary.
* User Context
  * The `user_context.json` has a generic structure, any top level category can be used (`Locations`, `Characters`, `Funny Hair Styles`)
  and individual entities within that category just need a `name` and `description` regardless of "what" they actually are.

## Experimental Features
* Document Extraction - Enabled via the `document_extraction` flag.