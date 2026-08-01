"""Collecteur Lever (API publique des postings, sans cle)."""
from collectors.base import Collector, http_get, make_offer_id


def _ms_to_iso(ms):
    try:
        from datetime import datetime, timezone
        return datetime.fromtimestamp(float(ms) / 1000.0, tz=timezone.utc).isoformat()
    except Exception:
        return ""


class LeverCollector(Collector):
    ats_type = "lever"

    def fetch(self):
        offers = []
        for c in self.companies:
            slug = (c.get("ats_slug") or "").strip()
            if not slug:
                continue
            r = http_get(f"https://api.lever.co/v0/postings/{slug}", params={"mode": "json"})
            if not r:
                continue
            try:
                data = r.json()
            except Exception:
                continue
            if not isinstance(data, list):
                continue
            for j in data:
                cats = j.get("categories") or {}
                iso = _ms_to_iso(j.get("createdAt"))
                offers.append({
                    "company": c.get("name") or slug,
                    "title": j.get("text", ""),
                    "url": j.get("hostedUrl", ""),
                    "location": cats.get("location", ""),
                    "date": iso[:10] if iso else "",
                    "published_at": iso,
                    "source": "lever",
                    "offer_id": make_offer_id("lever", slug, j.get("id"), j.get("hostedUrl", "")),
                    "description": j.get("descriptionPlain", "") or "",
                })
        return offers
