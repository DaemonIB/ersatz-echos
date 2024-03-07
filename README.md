# Ersatz Echos

## Running

### Dev
Copy `user_context.example.json` to `user_context.json`
Copy `config.example.json` to `config.json`
Run ```python main.py --events 10 --output history.json```

### Prod
Copy `user_context.example.json` to `user_context.json`
Copy `config.example.json` to `config.json`
If you want to provide some information to the LLM to base its timeline off of do the following:
1. Copy `user_context.example.json` to `user_context.json`
2. Edit `user_context.json` as needed and replace the sample data with your own data
Edit `config.json` replace `YOUR_API_KEY_HERE` with your LLM API key
Run `ersatz_echos.exe`

## Compiling
Run ```compile.bat```
This will create an `.exe` file in the `dist` folder and copy it to the working directory.