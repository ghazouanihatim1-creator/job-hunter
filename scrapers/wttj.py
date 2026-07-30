"""
Scraper Welcome To The Jungle via l'API Algolia publique.
Correctif : on ne demande plus que les stages (retrait de full_time) et on
applique le filtre stage/PFE + fraîcheur.
"""

from scrapers.base import BaseScraper
from config.settings import TARGET_KEYWORDS


class WTTJScraper(BaseScraper):
    def __init__(self):
        super().__init__("Welcome To The Jungle")

    def fetch_jobs(self) -> list:
        print(f"🔍 [{self.name}] Recherche d'offres en cours...")
        jobs = []
        url = ("https://a3y31ik27y-dsn.algolia.net/1/indexes/WW_JOBS_FR/query"
               "?x-algolia-agent=Algolia%20for%20JavaScript%20(4.14.2)"
               "&x-algolia-api-key=87042a9693bc2f5238bc35d4ac91a454"
               "&x-algolia-application-id=A3Y31IK27Y")

        keywords = ["M&A", "Transaction Services", "Private Equity", "Corporate Finance",
                    "FP&A", "Valuation", "Investment Banking"]

        for kw in keywords:
            payload = {
                "query": kw,
                "hitsPerPage": 20,
                "filters": "contract_type:internship",  # stages uniquement
            }
            res = self.safe_get(url, json_body=payload)
            if not (res and res.status_code == 200):
                continue
            try:
                for hit in res.json().get("hits", []):
                    title = hit.get("name", "Offre Finance")
                    company = (hit.get("company") or {}).get("name", "")
                    company_slug = (hit.get("company") or {}).get("slug", "")
                    slug = hit.get("slug", "")
                    office = hit.get("office") or {}
                    location = office.get("city") or "France"
                    job_url = f"https://www.welcometothejungle.com/fr/companies/{company_slug}/jobs/{slug}"
                    description = (hit.get("description") or "")[:500]

                    if not self.is_valid_job(title, description):
                        continue

                    jobs.append({
                        "title": title,
                        "company": company or "Entreprise WTTJ",
                        "location": location,
                        "url": job_url,
                        "date": "Récemment",
                        "description": description or "Offre publiée sur Welcome To The Jungle.",
                        "source": "Welcome To The Jungle",
                    })
            except Exception as e:
                print(f"❌ Erreur parsing WTTJ : {e}")

        print(f"✅ [{self.name}] {len(jobs)} offres stage/PFE extraites.")
        return jobs
