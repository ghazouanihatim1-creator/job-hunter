"""
Scraper LinkedIn via Google X-Ray (Recherche ciblée sans blocage ni compte).
"""

from scrapers.base import BaseScraper
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime

class LinkedInXRayScraper(BaseScraper):
    def __init__(self):
        super().__init__("LinkedIn Google X-Ray")

    def fetch_jobs() -> list[dict]:
        print(f"🔍 [{self.name}] Recherche Google X-Ray LinkedIn en cours...")
        jobs = []

        # Requêtes X-Ray ultra-ciblées sur LinkedIn Jobs
        queries = [
            'site:linkedin.com/jobs/view "stage" "M&A" OR "Transaction Services" France',
            'site:linkedin.com/jobs/view "stage" "FP&A" OR "Corporate Finance" France',
            'site:linkedin.com/jobs/view "internship" "Investment Banking" Luxembourg OR Switzerland'
        ]

        for query in queries:
            encoded_query = urllib.parse.quote(query)
            # Utilisation de DuckDuckGo / Google HTML sans JS pour extraction propre
            search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            res = self.safe_get(search_url)
            if res and res.status_code == 200:
                soup = BeautifulSoup(res.text, "lxml")
                results = soup.find_all("a", class_="result__url")
                
                for r in results:
                    href = r.get("href", "")
                    # Extraction du vrai lien LinkedIn
                    if "linkedin.com/jobs/view" in href:
                        # Nettoyage de l'URL issue de la redirection DuckDuckGo
                        if "uddg=" in href:
                            actual_url = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
                        else:
                            actual_url = href

                        parent = r.find_parent("div", class_="result__body")
                        title_elem = parent.find("a", class_="result__title") if parent else None
                        snippet_elem = parent.find("a", class_="result__snippet") if parent else None

                        title_text = title_elem.text.strip() if title_elem else "Offre Finance LinkedIn"
                        snippet_text = snippet_elem.text.strip() if snippet_elem else "Détails de l'offre sur LinkedIn."

                        jobs.append({
                            "title": title_text,
                            "company": "Entreprise sur LinkedIn",
                            "location": "France / Europe",
                            "url": actual_url,
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "description": snippet_text,
                            "source": "LinkedIn (Google X-Ray)"
                        })

        print(f"✅ [{self.name}] {len(jobs)} offres extraites.")
        return jobs
