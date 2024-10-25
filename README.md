
# CraftData
This project aims to develop a web-scraper designed to extract data from the entire Minecraft Wiki. The collected data will be structured into a dataset suitable for training large language models or what ever you want to do with it. The scraper will navigate through the all the sections of the wiki, capturing information about game mechanics, items, mobs, crafting recipes, etc. It can be used for other game wiki's too. (not tested right now)

# How Does It Work?
The scraper operates by first extracting all the links to the relevant web pages that contain information. It then retrieves the HTML content from these pages, cleans and passes it to a large language model for further processing.


## Installation

#### Clone the github repo:
```bash
 git clone https://github.com/Parkourer10/CraftData.git
```
---

#### Navigate to the project directory:
```bash
 cd CraftData
```
---

#### Install all the dependencies:

PYTHON:
```bash
 pip install -r requirements.txt
```

OLLAMA:
- https://ollama.com/download
- Install llama3.2 1b
```bash
 ollama pull llama3.2:1b
```
---
#### Change the config file: (IMPORTANT!)
Change the variables to scrape the approriate wiki/change output dataset name or model name or uploading to huggingface.

---
#### Run the project:
```bash
 python main.py
```


## Dataset structure:
```json
[
    {
        "url": "example.com"
        "question": "question",
        "answer": "answer"
    }
]

```




