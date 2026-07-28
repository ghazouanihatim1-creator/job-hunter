"""
Scraper LinkedIn via Google RSS avec filtres de qualité stricts.
"""

from scrapers.base import BaseScraper
import xml.etree.ElementTree as ET
import urllib.parse

class LinkedInXRayScraper(BaseScraper):
    def __init__(self):
        super().__init__("LinkedIn Google X-Ray")

    def fetch_jobs(self) -> list[dict]:
        print(f"🔍 [{self.name}] Recherche d'offres ciblées en cours...")
        jobs = []

        # Mots-clés de recherche très précis
        queries = [
            'site:linkedin.com/jobs/view "stage" "M&A" France "2027"',
            'site:linkedin.com/jobs/view "stage" "Transaction Services" France "2027"',
            'site:linkedin.com/jobs/view "stage" "Corporate Finance" France "2027"',
            'site:linkedin.com/jobs/view "stage" "FP&A" France "2027"'
        ]

        for query in queries:
            encoded = urllib.parse.quote(query)
            rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=fr&gl=FR&ceid=FR:fr"
            
            res = self.safe_get(rss_url)
            if res and res.status_code == 200:
                try:
                    root = ET.fromstring(res.text)
                    for item in root.findall(".//item")[:10]:
                        title = item.find("title").text if item.find("title") is not None else ""
                        link = item.find("link").text if item.find("link") is not None else ""
                        pub_date = item.find("pubDate").text[:16] if item.find("pubDate") is not None else "Récemment"

                        # Filtrage strict avant ajout
                        if self.is_valid_job(title, f"Publication {pub_date}"):
                            jobs.append({
                                "title": title,
                                "company": "Voir détails sur LinkedIn",
                                "location": "France",
                                "url": link,
                                "date": pub_date,
                                "description": f"Offre ciblée Finance : {title}",
                                "source": "LinkedIn"
                            })
                except Exception as e:
                    print(f"❌ Erreur parsing RSS LinkedIn : {e}")

        print(f"✅ [{self.name}] {len(jobs)} offres filtrées et validées.")
        return jobs
