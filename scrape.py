import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
import time
from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException

def scraper(website):
    chrome_driver_path = './chromedriver' #make sure to download chrome driver for your chrome version!!!
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  
    options.add_argument('--no-sandbox')  
    options.add_argument('--disable-dev-shm-usage')  
    
    while True:
        try:
            driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)
            response = requests.get(website)
            response.raise_for_status()
            html = response.text
            
            driver.get(website)
            time.sleep(1) #allow time for js or the page to load ig
            
            return html
        except RequestException as e:
            print(f"Connection failed: {str(e)}. Retrying...")
            time.sleep(5)
        except Exception as e:
            ValueError(f"Error in scraper: {str}")
            return None
        finally:
            if 'driver' in locals():
                driver.quit()
def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""

def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")

    for script_or_style in soup(["script", "style"]): 
        script_or_style.extract()
    
    cleaned_content = soup.get_text(separator='\n')
    cleaned_content = "\n".join(

        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    return cleaned_content

def split_dom_content(dom_content, max_length=2048): #u can change the max length to a greater value depending on your model
    return [
        dom_content[i : i + max_length] for i in range(0, len(dom_content), max_length)
    ]

def read_links_from_file(filename):
    links = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                
                line = line.strip()
                if line:
                    links.append(line)
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return links

def wikilinks(base_url, output_file):
    
    all_pages = set()
    
    to_visit = [base_url]
    
    visited = set()

    print(f"Starting to scrape {base_url}")
    
    try:
        while to_visit:
            current_url = to_visit.pop(0)
            
            if current_url in visited:
                continue
                
            visited.add(current_url)
            
            print(f"extracting: {current_url}")
            
            try:
                response = requests.get(current_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
               
                for link in soup.find_all('a'):
                    
                    href = link.get('href')
                    if href:
                        
                        if href.startswith('/') and ':' not in href and '?' not in href:
                            full_url = base_url.rstrip('/') + href
                            all_pages.add(full_url)
                            if full_url not in visited:
                                to_visit.append(full_url)
                                
                
                
                
                
            except requests.RequestException as e:
                print(f"Error scraping {current_url}: {e}")
                continue
    
    except KeyboardInterrupt:
        exit()
    
    
    with open(output_file, 'w') as f:
        for page in sorted(all_pages):
            f.write(page + '\n')
    
    
    




    
