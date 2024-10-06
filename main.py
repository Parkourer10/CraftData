import json
from scrape import scraper, split_dom_content, clean_body_content, extract_body_content, wikilinks
from parse import parse_with_ollama
import time
from tqdm import tqdm


# File names
WIKI_BASE_URL = "https://minecraft.wiki/" #website name. you can change it btw
OUTPUT_FILE = "wiki_pages.txt" #file name of the wikilinks
output_json_name = 'qa_results.json' # The file where the Q&A results will be saved
# print('AAAAAAAA')
wikilinks(WIKI_BASE_URL, OUTPUT_FILE)

def read_links_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def process_link(url):
    try:
        
        html_content = scraper(url)
        
       
        body_content = extract_body_content(html_content)
        cleaned_content = clean_body_content(body_content)
        
        
        dom_chunks = split_dom_content(cleaned_content)
                
        # Parse for question
        question_description = "Extract the main question or problem being discussed in this text. Return only the question, no additional text."
        question = parse_with_ollama(dom_chunks, question_description)
        
        # Parse for answer
        answer_description = "Extract the solution or answer to the main question in this text. Return only the answer, no additional text."
        answer = parse_with_ollama(dom_chunks, answer_description)
        
        #dataset format lol
        return {
            "url": url,
            "question": question.strip(),
            "answer": answer.strip()
        }
    
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return None

def main():
    
    links = read_links_from_file(OUTPUT_FILE)
    results = []
    
    print(f"Processing {len(links)} links...")
    
    # progress bar
    for link in tqdm(links):
        result = process_link(link)
        if result:
            results.append(result)
        time.sleep(1)
    
    # Save results
    with open(output_json_name, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Processed {len(results)} links successfully. Results saved to {output_json_name}")

if __name__ == "__main__":
    main()
