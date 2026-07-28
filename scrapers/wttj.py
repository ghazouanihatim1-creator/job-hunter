"""
Scraper Welcome To The Jungle via les endpoints Algolia/Search publics.
"""

from scrapers.base import BaseScraper
from config.settings import TARGET_KEYWORDS

class WTTJScraper(BaseScraper):
    def __init__(self):
        super().__init__("Welcome To The Jungle")

    def fetch_jobs() -> list[dict]:
        print(f"🔍 [{self.name}] Recherche d'offres en cours...")
        jobs = []
        
        # Endpoints JSON publics de recherche WTTJ
        base_url = "https://www.welcometothejungle.com/api/v1/jobs"
        
        # Sélection de mots-clés prioritaires
        query_keywords = ["M&A", "Transaction Services", "FP&A", "Corporate Finance", "Investment Banking"]

        for kw in query_keywords:
            params = {
                "query": kw,
                "page": 1,
                "per_page": 15,
                "in_around_lat_lng": "48.8566,2.3522",  # Centré France / Europe
            }
            
            res = self.safe_get(base_url, params=params)
            if res and res.status_code == 200:
                try:
                    data = res.json()
                    for item in data.get("jobs", []):
                        title = item.get("name", "")
                        company = item.get("company", {}).get("name", "N/A")
                        office = item.get("office", {})
                        location = office.get("city", "France") if office else "France"
                        slug = item.get("slug", "")
                        company_slug = item.get("company", {}).get("slug", "")
                        
                        job_url = f"https://www.welcometothejungle.com/fr/companies/{company_slug}/jobs/{slug}"
                        created_at = item.get("created_at", "")[:10]
                        description = item.get("description", "") or "Offre de stage en finance sur WTTJ."

                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": location,
                            "url": job_url,
                            "date": created_at,
                            "description": description[:500],
                            "source": "Welcome To The Jungle"
                        })
                except Exception as e:
                    print(f"❌ Erreur parsing WTTJ pour '{kw}' : {e}")

        print(f"✅ [{self.name}] {len(jobs)} offres extraites.")
        return jobs
