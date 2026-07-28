"""
Scraper Welcome To The Jungle via l'API Algolia publique de WTTJ.
"""

from scrapers.base import BaseScraper

class WTTJScraper(BaseScraper):
    def __init__(self):
        super().__init__("Welcome To The Jungle")

    def fetch_jobs(self) -> list[dict]:
        print(f"🔍 [{self.name}] Recherche d'offres en cours...")
        jobs = []

        # Algolia App ID & Key publics utilisés directement par le site WTTJ
        url = "https://a3y31ik27y-dsn.algolia.net/1/indexes/WW_JOBS_FR/query?x-algolia-agent=Algolia%20for%20JavaScript%20(4.14.2)&x-algolia-api-key=87042a9693bc2f5238bc35d4ac91a454&x-algolia-application-id=A3Y31IK27Y"

        keywords = ["M&A", "Transaction Services", "FP&A", "Corporate Finance"]

        for kw in keywords:
            payload = {
                "query": kw,
                "hitsPerPage": 10,
                "filters": "contract_type:internship OR contract_type:full_time"
            }
            
            res = self.safe_get(url, json_body=payload)
            if res and res.status_code == 200:
                try:
                    data = res.json()
                    for hit in data.get("hits", []):
                        title = hit.get("name", "Offre Finance")
                        company = hit.get("company", {}).get("name", "Entreprise WTTJ")
                        office = hit.get("office", {})
                        location = office.get("city", "France") if office else "France"
                        slug = hit.get("slug", "")
                        company_slug = hit.get("company", {}).get("slug", "")
                        
                        job_url = f"https://www.welcometothejungle.com/fr/companies/{company_slug}/jobs/{slug}"
                        
                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": location,
                            "url": job_url,
                            "date": "Récemment",
                            "description": hit.get("description", "Offre publiée sur Welcome To The Jungle.")[:500],
                            "source": "Welcome To The Jungle"
                        })
                except Exception as e:
                    print(f"❌ Erreur parsing WTTJ : {e}")

        print(f"✅ [{self.name}] {len(jobs)} offres extraites.")
        return jobs
