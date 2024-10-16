import json
import os 
from scrape import scraper, split_dom_content, clean_body_content, extract_body_content, wikilinks
from parse import parse_with_ollama, template
import time
from tqdm import tqdm

WIKI_BASE_URL = "https://minecraft.wiki/"  #website url
OUTPUT_FILE = "wiki_pages.txt"  #where the links will be saved
output_json_name = 'qa_results.json'  #the json file where the Q&A results will be saved
SNAPSHOT_INTERVAL = 10  #take a snapshot every 10 pages, you can change this value to take more or less snapshots

def read_links_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def process_link(url):
    try:
        html_content = scraper(url)  
        
        if not html_content:
            return []

        body_content = extract_body_content(html_content)
        cleaned_content = clean_body_content(body_content)
        
        dom_chunks = split_dom_content(cleaned_content)

        #parse for question
        question_description = "Extract the main question or problem being discussed in this text. Return only the question, no additional text. If there is no question, return {}."
        questions = parse_with_ollama(dom_chunks, question_description)

        #parse for answer
        answer_description = "Extract the solution or answer to the main question in this text. Return only the answer, no additional text. If there is no answer, return {}."
        answers = parse_with_ollama(dom_chunks, answer_description)

        #combine questions and answers
        results = []
        for q, a in zip(questions.split("\n"), answers.split("\n")):
            if q and a:  # Ensure both question and answer are present
                results.append({
                    "url": url,
                    "question": q.strip(),
                    "answer": a.strip()
                })

        return results
    
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return []

def save_snapshot(results, snapshot_number):
    snapshot_file = f'snapshot_{snapshot_number}.json'
    with open(snapshot_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Snapshot saved: {snapshot_file}")

def main():
    if not os.path.exists(OUTPUT_FILE):
        wikilinks(WIKI_BASE_URL, OUTPUT_FILE)
    else:
        print(f"Using existing file {OUTPUT_FILE}.")

    links = read_links_from_file(OUTPUT_FILE)
    results = []

    print(f"Processing {len(links)} links...")

    for i, link in enumerate(tqdm(links), 1):
        link_results = process_link(link)
        if link_results:
            results.extend(link_results)

        if i % SNAPSHOT_INTERVAL == 0:
            save_snapshot(results, i // SNAPSHOT_INTERVAL)

        time.sleep(1)

    #save :D
    with open(output_json_name, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Processed {len(results)} Q&A pairs successfully. Results saved to {output_json_name}")

if __name__ == "__main__":
    main()