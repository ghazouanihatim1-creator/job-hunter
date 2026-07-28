"""
Scraper JobTeaser Public via Recherche Ciblée.
"""

from scrapers.base import BaseScraper
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime

class JobTeaserScraper(BaseScraper):
    def __init__(self):
        super().__init__("JobTeaser Public")

    def fetch_jobs(self) -> list[dict]:
        print(f"🔍 [{self.name}] Recherche JobTeaser en cours...")
        jobs = []

        queries = [
            'site:jobteaser.com/fr/job-offers "stage" "M&A" OR "Transaction Services"',
            'site:jobteaser.com/fr/job-offers "stage" "FP&A" OR "Finance"'
        ]

        for query in queries:
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            res = self.safe_get(search_url)
            if res and res.status_code == 200:
                soup = BeautifulSoup(res.text, "lxml")
                results = soup.find_all("a", class_="result__url")
                
                for r in results:
                    href = r.get("href", "")
                    if "jobteaser.com" in href and "job-offers" in href:
                        if "uddg=" in href:
                            actual_url = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
                        else:
                            actual_url = href

                        parent = r.find_parent("div", class_="result__body")
                        title_elem = parent.find("a", class_="result__title") if parent else None
                        snippet_elem = parent.find("a", class_="result__snippet") if parent else None

                        title_text = title_elem.text.strip() if title_elem else "Offre JobTeaser"
                        snippet_text = snippet_elem.text.strip() if snippet_elem else "Détails sur JobTeaser."

                        jobs.append({
                            "title": title_text,
                            "company": "Recruteur JobTeaser",
                            "location": "France",
                            "url": actual_url,
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "description": snippet_text,
                            "source": "JobTeaser Public"
                        })

        print(f"✅ [{self.name}] {len(jobs)} offres extraites.")
        return jobs
