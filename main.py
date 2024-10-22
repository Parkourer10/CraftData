import json
import os 
import time
from tqdm import tqdm
from huggingface_hub import HfApi, create_repo, upload_file, login
from scrape import scraper, extract_body_content, clean_body_content, wikilinks
from parse import process_content

BASE_URL = "https://minecraft.wiki/"  #you can enter the URL of the game wiki you want to scrape.
OUTPUT_FILE = "wiki_links.txt"  #you can change this; it doesn't matter what name.
output_json_name = 'dataset.json'  #you can change the name of the dataset too.
HF_DATASET = False#set to False to disable upload, or (True, "your_token", "your_dataset_name") to enable
SNAPSHOTS = False  #set to False to disable snapshots, or (True, interval) to enable (e.g., (True, 100))

def read_links_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def process_link(url):
    try:
        html_content = scraper(url)  
        if not html_content:
            return None

        body_content = extract_body_content(html_content)
        cleaned_content = clean_body_content(body_content)
        
        qa_pairs = process_content([cleaned_content])
        return [{"url": url, "question": q, "answer": a} for q, a in qa_pairs]
    
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return None

def save_snapshot(results, snapshot_number):
    if isinstance(SNAPSHOTS, tuple) and SNAPSHOTS[0]:
        snapshot_file = f'snapshot_{snapshot_number}.json'
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Snapshot saved: {snapshot_file}")

def upload_to_huggingface(HF_DATASET, local_file_path):

    if not HF_DATASET or not isinstance(HF_DATASET, tuple) or HF_DATASET[0] is False:
        print("Upload to Hugging Face is disabled.")
        return

    hf_token, dataset_name = HF_DATASET[1], HF_DATASET[2]

    
    login(token=hf_token) 

    api = HfApi()
    hf_username = api.whoami()["name"]
    repo_id = f"{hf_username}/{dataset_name}"
    
    try:
        api.repo_info(repo_id=repo_id)
        print(f"Repo {repo_id} already exists.")
    except Exception:
        print(f"Repo {repo_id} doesn't exist, creating it now.")
        create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True)

    #upload to repo
    upload_file(
        path_or_fileobj=local_file_path,
        path_in_repo="dataset.json",
        repo_id=repo_id,
        repo_type="dataset"
    )

    print(f"Uploaded {local_file_path} to {repo_id}/dataset.json")

def main():
    if not os.path.exists(OUTPUT_FILE):
        wikilinks(BASE_URL, OUTPUT_FILE)
    else:
        print(f"Using existing file {OUTPUT_FILE}.")

    links = read_links_from_file(OUTPUT_FILE)
    results = []

    print(f"Processing {len(links)} links...")

    for i, link in enumerate(tqdm(links), 1):
        link_results = process_link(link)
        if link_results:
            results.extend(link_results)

        if isinstance(SNAPSHOTS, tuple) and SNAPSHOTS[0] and i % SNAPSHOTS[1] == 0:
            save_snapshot(results, i // SNAPSHOTS[1])

        time.sleep(1)

    with open(output_json_name, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Processed {len(results)} question-answer pairs successfully. Results saved to {output_json_name}")

    # Upload to Hugging Face if enabled
    if isinstance(HF_DATASET, tuple) and HF_DATASET[0]:
        upload_to_huggingface(HF_DATASET, output_json_name)

if __name__ == "__main__":
    main()
