# ATUI - Assistant Textual User Interface
 
# How to use

## Setup

```bash
pyenv install 3.12.0                # install python version
pyenv local 3.12.0                  # set python version
python -m venv venv                 # create virtual environment
source ./venv/bin/activate          # activate virtual environment
pip3 install -r requirements.txt    # install dependencies
```

## Run

```bash
export OPENAI_API_KEY=sk-....   # set openai api key. alternatively, create a .env file with this key
python main.py
```

# Features

- [x] Textual User Interface    
    - [x] Assistant
        - [ ] Create
        - [x] Select
        - [x] Details
    - [x] Thread
        - [x] Create
        - [x] Select
        - [x] Details
    - [x] Message
        - [x] List
        - [ ] Annotations
        - [ ] Attachments
    - [x] Tools
        - [x] Code Interpreter
        - [x] Retrieve
        - [ ] Function
    - [x] Debug: Message / Runs / Steps
    - [x] Log

- [x] Domain
    - [x] Assistant
        - [x] Create
        - [x] Retrieve
        - [x] Delete
        - [x] List All
        - [ ] Update
        - [ ] Files
    - [x] Thread
        - [x] Create
        - [x] Retrieve
        - [x] Delete
        - [x] List All
        - [ ] Update
        - [x] Retrieve Messages
        - [x] Events
            - [x] New Message
        - [x] Persist
            - [x] Local
            - [ ] DB
    - [x] Message
        - [x] Create
        - [x] Retrieve
        - [ ] Update
        - [ ] Files
    - [x] Run
        - [x] Create
        - [x] Retrieve
        - [x] Cancel
        - [ ] List All
        - [ ] Update
        - [x] Polling
        - [x] Events
            - [x] Status Change
    - [x] Step
        - [x] Types
            - [x] Message Creation
            - [x] Tool Call
        - [x] Retrieve
        - [x] Polling
        - [x] Events
            - [x] New Step
            - [x] Status Change
    - [x] Tools
        - [x] Code Interpreter
        - [x] Retrieve
        - [x] Function
            - [ ] Handle Function Call