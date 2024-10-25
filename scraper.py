import asyncio
import aiohttp
from bs4 import BeautifulSoup
from collections import deque
import logging
from typing import Set
from config import SCRAPING_TIMEOUT, MAX_CONCURRENT_SCRAPES
#configuring logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AsyncWikiScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.visited = set()
        self.all_pages = set()
        self.session = None
        
    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        if self.session:
            await self.session.close()
            
    async def fetch_page(self, url: str) -> str:
        try:
            async with self.session.get(url, timeout=SCRAPING_TIMEOUT) as response:
                if response.status == 200:
                    return await response.text()
                logger.warning(f"Failed to fetch {url}: Status {response.status}")
                return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def extract_links(self, html: str, current_url: str) -> Set[str]:
        if not html:
            return set()
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and href.startswith('/') and ':' not in href and '?' not in href:
                full_url = self.base_url + href
                links.add(full_url)
        return links

    async def scrape_site(self):
        await self.init_session()
        to_visit = deque([self.base_url])
        
        while to_visit:
            batch = []
            while to_visit and len(batch) < MAX_CONCURRENT_SCRAPES:
                url = to_visit.popleft()
                if url not in self.visited:
                    batch.append(url)
                    self.visited.add(url)
            
            if not batch:
                continue
            tasks = [self.fetch_page(url) for url in batch]
            htmls = await asyncio.gather(*tasks)
            for url, html in zip(batch, htmls):
                if html:
                    new_links = self.extract_links(html, url)
                    self.all_pages.update(new_links)
                    to_visit.extend(new_links - self.visited)
                    
        return sorted(self.all_pages)