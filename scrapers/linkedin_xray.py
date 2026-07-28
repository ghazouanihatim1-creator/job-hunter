"""
Scraper LinkedIn ultra-frais (< 7 jours).
"""

from scrapers.base import BaseScraper
import xml.etree.ElementTree as ET
import urllib.parse

class LinkedInXRayScraper(BaseScraper):
    def __init__(self):
        super().__init__("LinkedIn Google X-Ray")

    def fetch_jobs(self) -> list[dict]:
        print(f"🔍 [{self.name}] Recherche d'offres ultra-récentes (< 7 jours)...")
        jobs = []

        # 'when:7d' force Google à restreindre aux 7 derniers jours
        queries = [
            'site:linkedin.com/jobs/view "stage" "M&A" France when:7d',
            'site:linkedin.com/jobs/view "stage" "Transaction Services" France when:7d',
            'site:linkedin.com/jobs/view "stage" "Corporate Finance" France when:7d',
            'site:linkedin.com/jobs/view "stage" "FP&A" France when:7d'
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

                        # Filtre strict : Mots-clés + Date <= 7 jours
                        if self.is_valid_job(title, f"Publication {pub_date}", pub_date):
                            jobs.append({
                                "title": title,
                                "company": "Voir détails sur LinkedIn",
                                "location": "France",
                                "url": link,
                                "date": pub_date,
                                "description": f"Offre très récente (< 7 jours) : {title}",
                                "source": "LinkedIn"
                            })
                except Exception as e:
                    print(f"❌ Erreur parsing RSS LinkedIn : {e}")

        print(f"✅ [{self.name}] {len(jobs)} offres ultra-récentes validées.")
        return jobs
