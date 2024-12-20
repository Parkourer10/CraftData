#config.py
MODEL = "llama3.2:1b" #can change this IG
MAX_CONCURRENT_OLLAMA = 3 #amount of ollama insances to run at once, can be changed
BASE_URL = ""  #base url for wiki
OUTPUT_FILE = "links.txt"  #name of the file that will contain the links to be scraped
OUTPUT_JSON = "dataset.json"  #name of the dataset json file which will be created after scraping
SCRAPING_TIMEOUT = 30  #scraping timeout in seconds, if a page takes longer than this, it will be skipped
MAX_CONCURRENT_SCRAPES = 10 #change this to a higher value if you want to scrape more urls at once
HF_DATASET = False  #to upload the dataset to hf hub. To upload it do: (True, "hf_xxxxx", "name of the dataset lol")

summary_template = """
Summarize the main content of this webpage about the game very concisely in as many paragraphs you have to. Focus on the most important information and key points:
{dom_content}
Summary:
"""

questions_template = """
Based on the following summary about the related topic, generate atleast 5-10 several diverse, detailed and unique important questions that capture various aspects of the main topic. Your output should strictly follow these rules:
1. Each question must be on its own line with no prefixes (no numbers, bullets, or asterisks)
2. Each question must cover a unique aspect of the summary
3. Questions must be clear, concise, and directly related to Minecraft
4. Questions must be complete sentences ending with a question mark
5. No meta-text, formatting, or additional commentary
6. No questions about versions unless explicitly mentioned in the summary
7. No questions about licensing or website liscensing.
8. Dont say that you are using a summary.
Here's the summary:
{summary}
Questions:"""

answer_template = """
Provide a concise, factual answer to the following question based on the summary about the game. The answer should be informative and directly address the question without asking for further clarification or posing new questions. Do not include unicode characters. Do not say that you are using a summary
Summary: {summary}
Question: {question}
Answer:
"""
