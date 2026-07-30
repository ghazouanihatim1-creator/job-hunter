"""
Scraper des boards ATS des entreprises de la watchlist.

Lit companies.csv et, pour chaque boîte dont l'ATS a été détecté (colonnes
`ats` + `slug` remplies par l'enrichissement), interroge son board public :
Greenhouse, Lever, Ashby, SmartRecruiters. Ne garde que les stages/PFE finance.

Tant que l'enrichissement n'a pas tourné, ce scraper ne renvoie rien (aucune
boîte n'a encore d'ATS renseigné) — c'est normal.
"""

from scrapers.base import BaseScraper
from utils.companies import get_registry
from config.settings import TARGET_KEYWORDS


class CompanyBoardsScraper(BaseScraper):
    def __init__(self):
        super().__init__("Company ATS Boards")
        self.registry = get_registry()

    # --- Endpoints par ATS ---
    def _greenhouse(self, slug):
        url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
        res = self.safe_get(url)
        if not (res and res.status_code == 200):
            return []
        out = []
        for j in res.json().get("jobs", []):
            out.append({
                "title": j.get("title", ""),
                "location": (j.get("location") or {}).get("name", ""),
                "url": j.get("absolute_url", ""),
                "description": (j.get("content", "") or "")[:600],
                "date": (j.get("updated_at", "") or "")[:10],
            })
        return out

    def _lever(self, slug):
        url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
        res = self.safe_get(url)
        if not (res and res.status_code == 200):
            return []
        out = []
        for j in res.json():
            out.append({
                "title": j.get("text", ""),
                "location": (j.get("categories") or {}).get("location", ""),
                "url": j.get("hostedUrl", ""),
                "description": (j.get("descriptionPlain", "") or "")[:600],
                "date": "Récemment",
            })
        return out

    def _ashby(self, slug):
        url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
        res = self.safe_get(url)
        if not (res and res.status_code == 200):
            return []
        out = []
        for j in res.json().get("jobs", []):
            out.append({
                "title": j.get("title", ""),
                "location": j.get("location", ""),
                "url": j.get("jobUrl", ""),
                "description": (j.get("descriptionPlain", "") or "")[:600],
                "date": "Récemment",
            })
        return out

    def _smartrecruiters(self, slug):
        url = f"https://api.smartrecruiters.com/v1/companies/{slug}/postings"
        res = self.safe_get(url)
        if not (res and res.status_code == 200):
            return []
        out = []
        for j in res.json().get("content", []):
            loc = j.get("location", {}) or {}
            out.append({
                "title": j.get("name", ""),
                "location": loc.get("city", ""),
                "url": f"https://jobs.smartrecruiters.com/{slug}/{j.get('id','')}",
                "description": "",
                "date": (j.get("releasedDate", "") or "")[:10],
            })
        return out

    DISPATCH = {
        "greenhouse": _greenhouse,
        "lever": _lever,
        "ashby": _ashby,
        "smartrecruiters": _smartrecruiters,
    }

    def _is_finance_role(self, text: str) -> bool:
        low = text.lower()
        return any(kw in low for kw in TARGET_KEYWORDS)

    def fetch_jobs(self) -> list:
        print(f"🔍 [{self.name}] Interrogation des boards ATS...")
        jobs = []
        enriched = [r for r in self.registry.rows if r.get("ats") and r.get("slug")]
        print(f"   {len(enriched)} entreprise(s) avec ATS détecté à interroger.")

        for row in enriched:
            ats = (row.get("ats") or "").lower().strip()
            slug = (row.get("slug") or "").strip()
            handler = self.DISPATCH.get(ats)
            if not handler:
                continue
            try:
                postings = handler(self, slug)
            except Exception as e:
                print(f"   ⚠️ {row['name']} ({ats}) : {e}")
                continue

            for p in postings:
                title = p.get("title", "")
                if not self.is_valid_job(title, p.get("description", ""), p.get("date", "")):
                    continue
                if not self._is_finance_role(f"{title} {p.get('description','')}"):
                    continue
                jobs.append({
                    "title": title,
                    "company": row["name"],
                    "location": p.get("location") or "Voir offre",
                    "url": p.get("url", ""),
                    "date": p.get("date", "Récemment"),
                    "description": p.get("description", "") or f"Stage finance chez {row['name']}.",
                    "source": f"ATS {ats.capitalize()}",
                })

        print(f"✅ [{self.name}] {len(jobs)} offre(s) stage/PFE finance extraites.")
        return jobs
