# textual-assistant
 
# dev setup

```bash
pyenv install 3.12.0                # install python version
pyenv local 3.12.0                  # set python version
python -m venv venv                 # create virtual environment
source ./venv/bin/activate          # activate virtual environment
pip3 install -r requirements.txt    # install dependencies
```

# run

```bash
export OPENAI_API_KEY=sk-....   # set openai api key. alternatively, create a .env file with this key
python main.py
```
