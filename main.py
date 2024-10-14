import json
import os 
from scrape import scraper, split_dom_content, clean_body_content, extract_body_content, wikilinks
from parse import parse_with_ollama
import time
import requests 
from tqdm import tqdm

WIKI_BASE_URL = "https://minecraft.wiki/"  #website url
OUTPUT_FILE = "wiki_pages.txt"  #where the links will be saved
output_json_name = 'qa_results.json'  #the json file where the Q&A results will be saved


def retry_request(url):
    while True: #idk if this function will cause problems:)
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except (requests.ConnectionError, requests.Timeout):
            print(f"Connection failed. Retrying...")
            time.sleep(5)

def read_links_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def process_link(url):
    try:
        html_content = retry_request(url)
        
        if not html_content:
            return None

        body_content = extract_body_content(html_content)
        cleaned_content = clean_body_content(body_content)
        
        dom_chunks = split_dom_content(cleaned_content)
                
        #parse for question
        question_description = "Extract the main question or problem being discussed in this text. Return only the question, no additional text."
        question = parse_with_ollama(dom_chunks, question_description)
        
        #parse for answer
        answer_description = "Extract the solution or answer to the main question in this text. Return only the answer, no additional text."
        answer = parse_with_ollama(dom_chunks, answer_description)
        
        return {
            "url": url,
            "question": question.strip(),
            "answer": answer.strip()
        }
    
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return None

def main():
    #check if the output file alr exists to not waste time
    if not os.path.exists(OUTPUT_FILE):
        print(f"{OUTPUT_FILE} not found. Scraping links from {WIKI_BASE_URL}.")
        wikilinks(WIKI_BASE_URL, OUTPUT_FILE)
    else:
        print(f"Using existing file {OUTPUT_FILE}.")

    links = read_links_from_file(OUTPUT_FILE)
    results = []

    print(f"Processing {len(links)} links...")

    for link in tqdm(links):
        result = process_link(link)
        if result:
            results.append(result)
        time.sleep(1)
    
    
    with open(output_json_name, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Processed {len(results)} links successfully. Results saved to {output_json_name}")

if __name__ == "__main__":
    main()
