"""Collecteur SmartRecruiters (API publique des postings, sans cle)."""
from collectors.base import Collector, http_get, make_offer_id


class SmartRecruitersCollector(Collector):
    ats_type = "smartrecruiters"

    def fetch(self):
        offers = []
        for c in self.companies:
            slug = (c.get("ats_slug") or "").strip()
            if not slug:
                continue
            r = http_get(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings",
                         params={"limit": 100})
            if not r:
                continue
            try:
                content = r.json().get("content", [])
            except Exception:
                continue
            for j in content:
                loc = j.get("location") or {}
                locstr = ", ".join(x for x in [loc.get("city"), loc.get("country")] if x)
                pid = j.get("id")
                offers.append({
                    "company": c.get("name") or slug,
                    "title": j.get("name", ""),
                    "url": f"https://jobs.smartrecruiters.com/{slug}/{pid}",
                    "location": locstr,
                    "date": (j.get("releasedDate", "") or "")[:10],
                    "published_at": j.get("releasedDate", ""),
                    "source": "smartrecruiters",
                    "offer_id": make_offer_id("smartrecruiters", slug, pid, ""),
                    "description": j.get("name", ""),
                })
        return offers
