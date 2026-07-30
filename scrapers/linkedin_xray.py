"""
Scraper LinkedIn ultra-frais (< 7 jours) via Google News RSS.
Correctif : on tente d'extraire le nom d'entreprise depuis le titre RSS
(format habituel "Titre du poste - Entreprise - Lieu") pour permettre le
matching sur la watchlist et l'auto-découverte.
"""

from scrapers.base import BaseScraper
import xml.etree.ElementTree as ET
import urllib.parse


class LinkedInXRayScraper(BaseScraper):
    def __init__(self):
        super().__init__("LinkedIn Google X-Ray")

    def _extract_company(self, title: str) -> str:
        # Les titres Google News se terminent souvent par " - Source"
        cleaned = title.rsplit(" - ", 1)[0] if " - " in title else title
        # Format LinkedIn fréquent : "Poste - Entreprise - Ville"
        parts = [p.strip() for p in cleaned.split(" - ")]
        if len(parts) >= 2:
            return parts[1]
        return ""

    def fetch_jobs(self) -> list:
        print(f"🔍 [{self.name}] Recherche d'offres ultra-récentes (< 7 jours)...")
        jobs = []
        queries = [
            'site:linkedin.com/jobs/view ("stage" OR "stagiaire" OR "PFE") "M&A" France when:7d',
            'site:linkedin.com/jobs/view ("stage" OR "stagiaire" OR "PFE") "Transaction Services" France when:7d',
            'site:linkedin.com/jobs/view ("stage" OR "stagiaire" OR "PFE") "Private Equity" France when:7d',
            'site:linkedin.com/jobs/view ("stage" OR "stagiaire" OR "PFE") "Corporate Finance" France when:7d',
            'site:linkedin.com/jobs/view ("stage" OR "stagiaire") "Valuation" France when:7d',
        ]

        for query in queries:
            encoded = urllib.parse.quote(query)
            rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=fr&gl=FR&ceid=FR:fr"
            res = self.safe_get(rss_url)
            if not (res and res.status_code == 200):
                continue
            try:
                root = ET.fromstring(res.text)
                for item in root.findall(".//item")[:12]:
                    title = item.findtext("title", "")
                    link = item.findtext("link", "")
                    pub_date = (item.findtext("pubDate", "") or "Récemment")[:16]

                    if not self.is_valid_job(title, "", pub_date):
                        continue

                    jobs.append({
                        "title": title,
                        "company": self._extract_company(title) or "Voir détails sur LinkedIn",
                        "location": "France",
                        "url": link,
                        "date": pub_date,
                        "description": f"Offre récente (< 7 jours) : {title}",
                        "source": "LinkedIn",
                    })
            except Exception as e:
                print(f"❌ Erreur parsing RSS LinkedIn : {e}")

        print(f"✅ [{self.name}] {len(jobs)} offres validées.")
        return jobs
