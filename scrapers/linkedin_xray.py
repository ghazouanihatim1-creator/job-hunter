"""
Scraper LinkedIn via flux RSS / Reader.
"""

from scrapers.base import BaseScraper
import xml.etree.ElementTree as ET
import urllib.parse

class LinkedInXRayScraper(BaseScraper):
    def __init__(self):
        super().__init__("LinkedIn Google X-Ray")

    def fetch_jobs(self) -> list[dict]:
        print(f"🔍 [{self.name}] Recherche LinkedIn RSS en cours...")
        jobs = []

        queries = [
            'site:linkedin.com/jobs/view "stage" "M&A" France',
            'site:linkedin.com/jobs/view "stage" "Transaction Services" France',
            'site:linkedin.com/jobs/view "stage" "FP&A" France'
        ]

        for query in queries:
            encoded = urllib.parse.quote(query)
            rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=fr&gl=FR&ceid=FR:fr"
            
            res = self.safe_get(rss_url)
            if res and res.status_code == 200:
                try:
                    root = ET.fromstring(res.text)
                    for item in root.findall(".//item")[:5]:
                        title = item.find("title").text if item.find("title") is not None else "Offre LinkedIn"
                        link = item.find("link").text if item.find("link") is not None else ""
                        pub_date = item.find("pubDate").text[:16] if item.find("pubDate") is not None else "Récemment"

                        jobs.append({
                            "title": title,
                            "company": "Voir détails sur LinkedIn",
                            "location": "France",
                            "url": link,
                            "date": pub_date,
                            "description": f"Opportunité détectée : {title}",
                            "source": "LinkedIn (Google X-Ray)"
                        })
                except Exception as e:
                    print(f"❌ Erreur RSS LinkedIn : {e}")

        print(f"✅ [{self.name}] {len(jobs)} offres extraites.")
        return jobs
