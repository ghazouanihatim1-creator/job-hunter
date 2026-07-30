"""
Scraper JobTeaser via recherche ciblée DuckDuckGo (HTML).
Applique le filtre stage/PFE. Le nom d'entreprise n'est pas toujours
disponible ici : le matching/découverte se fera au centre.
"""

from scrapers.base import BaseScraper
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime


class JobTeaserScraper(BaseScraper):
    def __init__(self):
        super().__init__("JobTeaser Public")

    def fetch_jobs(self) -> list:
        print(f"🔍 [{self.name}] Recherche JobTeaser en cours...")
        jobs = []
        queries = [
            'site:jobteaser.com/fr/job-offers ("stage" OR "stagiaire" OR "PFE") ("M&A" OR "Transaction Services")',
            'site:jobteaser.com/fr/job-offers ("stage" OR "stagiaire") ("Private Equity" OR "Corporate Finance")',
            'site:jobteaser.com/fr/job-offers ("stage" OR "stagiaire") ("Valuation" OR "FP&A")',
        ]

        for query in queries:
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            res = self.safe_get(search_url)
            if not (res and res.status_code == 200):
                continue

            soup = BeautifulSoup(res.text, "lxml")
            for r in soup.find_all("a", class_="result__url"):
                href = r.get("href", "")
                if "jobteaser.com" not in href or "job-offers" not in href:
                    continue
                if "uddg=" in href:
                    actual_url = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
                else:
                    actual_url = href

                parent = r.find_parent("div", class_="result__body")
                title_elem = parent.find("a", class_="result__title") if parent else None
                snippet_elem = parent.find("a", class_="result__snippet") if parent else None
                title_text = title_elem.text.strip() if title_elem else "Offre JobTeaser"
                snippet_text = snippet_elem.text.strip() if snippet_elem else "Détails sur JobTeaser."

                if not self.is_valid_job(title_text, snippet_text):
                    continue

                jobs.append({
                    "title": title_text,
                    "company": "Recruteur JobTeaser",
                    "location": "France",
                    "url": actual_url,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "description": snippet_text,
                    "source": "JobTeaser",
                })

        print(f"✅ [{self.name}] {len(jobs)} offres extraites.")
        return jobs
