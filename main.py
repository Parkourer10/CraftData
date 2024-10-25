import asyncio
import aiohttp
import json
import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from parse import ContentProcessor
from huggingface_hub import HfApi, create_repo, upload_file, login
from config import BASE_URL, OUTPUT_FILE, OUTPUT_JSON, SCRAPING_TIMEOUT, HF_DATASET

def scrape_wiki_pages(base_url, output_file):
    all_pages = set()
    to_visit = [base_url]
    visited = set()
    print(f"Starting to scrape {base_url}")
    
    with open(output_file, 'w') as f:
        try:
            while to_visit:
                current_url = to_visit.pop(0)
                
                if current_url in visited:
                    continue
                
                visited.add(current_url)
                print(f"Scraping: {current_url}")
                
                try:
                    response = requests.get(current_url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    for link in soup.find_all('a'):
                        href = link.get('href')
                        if href:
                            if href.startswith('/') and ':' not in href and '?' not in href:
                                full_url = base_url.rstrip('/') + href
                                if full_url not in visited and full_url not in to_visit:
                                    all_pages.add(full_url)
                                    to_visit.append(full_url)
                                    
                                    f.write(full_url + '\n')
                                    f.flush()
                
                except requests.RequestException as e:
                    print(f"Error scraping {current_url}: {e}")
                    continue
            
        except KeyboardInterrupt:
            print("\nScraping interrupted")
    
    print(f"\nScraping completed. Found {len(all_pages)} unique pages.")
    print(f"Results saved to {output_file}")
    return sorted(all_pages)

async def upload_to_huggingface(file_path: str):
    if not HF_DATASET or not isinstance(HF_DATASET, tuple) or not HF_DATASET[0]:
        print("Upload to Hugging Face is disabled")
        return
        
    try:
        token, dataset_name = HF_DATASET[1], HF_DATASET[2]
        login(token=token)
        api = HfApi()
        user_info = api.whoami()
        username = user_info["name"]
        repo_id = f"{username}/{dataset_name}"
        
        print(f"Uploading dataset to {repo_id}...")
        
        try:
            api.repo_info(repo_id=repo_id)
            print(f"Repository {repo_id} already exists")
        except Exception:
            print(f"Creating new repository: {repo_id}")
            create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True)
        
        upload_file(
            path_or_fileobj=file_path,
            path_in_repo=os.path.basename(file_path),
            repo_id=repo_id,
            repo_type="dataset"
        )
        
        print(f"Successfully uploaded {file_path} to {repo_id}")
        print(f"Dataset is now available at: https://huggingface.co/datasets/{repo_id}")
        
    except Exception as e:
        print(f"Error uploading to Hugging Face Hub: {str(e)}")

async def main():
    if not os.path.exists(OUTPUT_FILE):
        print("Scraping site links...")
        links = scrape_wiki_pages(BASE_URL, OUTPUT_FILE)
    else:
        print("Reading existing links from file...")
        with open(OUTPUT_FILE, 'r') as f:
            links = [line.strip() for line in f if line.strip()]
            for link in links:
                print(f"Link: {link}")
    
    processor = ContentProcessor()
    async with aiohttp.ClientSession() as session:
        all_qa_pairs = []
        pbar = tqdm(total=len(links), desc="Processing pages", unit="pages")
        batch_size = 10  
        for i in range(0, len(links), batch_size):
            batch = links[i:i + batch_size]
            
            async def process_url(url):
                try:
                    async with session.get(url, timeout=SCRAPING_TIMEOUT) as response:
                        if response.status == 200:
                            content = await response.text()
                            return await processor.process_content(url, content)
                except Exception as e:
                    print(f"Error processing {url}")
                return None
            
            tasks = [process_url(url) for url in batch]
            batch_results = await asyncio.gather(*tasks)
            
            for result in batch_results:
                if result:
                    all_qa_pairs.extend(result)
            
            pbar.update(len(batch))
            
            with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                json.dump(all_qa_pairs, f, indent=2, ensure_ascii=False)
        
        pbar.close()
    
    print(f"\ndone! Generated {len(all_qa_pairs)} QA pairs")
    await upload_to_huggingface(OUTPUT_JSON)

if __name__ == "__main__":
    asyncio.run(main())