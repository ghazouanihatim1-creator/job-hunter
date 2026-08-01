"""Collecteur Greenhouse (API publique du job board, sans cle)."""
from collectors.base import Collector, http_get, make_offer_id, strip_html


class GreenhouseCollector(Collector):
    ats_type = "greenhouse"

    def fetch(self):
        offers = []
        for c in self.companies:
            slug = (c.get("ats_slug") or "").strip()
            if not slug:
                continue
            r = http_get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
                         params={"content": "true"})
            if not r:
                continue
            try:
                jobs = r.json().get("jobs", [])
            except Exception:
                continue
            for j in jobs:
                loc = (j.get("location") or {}).get("name", "")
                offers.append({
                    "company": c.get("name") or slug,
                    "title": j.get("title", ""),
                    "url": j.get("absolute_url", ""),
                    "location": loc,
                    "date": j.get("updated_at", ""),
                    "published_at": j.get("updated_at", ""),
                    "source": "greenhouse",
                    "offer_id": make_offer_id("greenhouse", slug, j.get("id"), j.get("absolute_url", "")),
                    "description": strip_html(j.get("content", "")),
                })
        return offers
