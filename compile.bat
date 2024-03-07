pip install -r requirements-dev.txt
python setup.py build_ext --inplace
pyinstaller --onefile --name ersatz_echos .\main.py
copy .\config.example.json .\dist\config.json
copy .\user_context.example.json .\dist\user_context.example.json
copy .\dist\ersatz_echos.exe ersatz_echos.exe
clean.bat