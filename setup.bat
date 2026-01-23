@echo off
echo Setting up Personal LLM...

python -m venv venv
call venv\Scripts\activate.bat

pip install -r requirements.txt

if not exist config.toml (
    copy config.toml.example config.toml
    echo Created config.toml - please edit it with your settings
)

echo Setup complete! Run: venv\Scripts\activate.bat then cd src and python main.py
