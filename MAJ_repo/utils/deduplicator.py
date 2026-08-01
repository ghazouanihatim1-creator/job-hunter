"""
Memoire anti-doublon v2 : dict {offer_id: {...}} avec dates.
Regle clef : une offre n'est marquee 'notifiee' qu'APRES un envoi Telegram reussi.
=> zero doublon (jamais renotifiee) ET rien perdu (re-evaluee tant que non notifiee).
"""
import json
import os
from datetime import datetime, timezone

SEEN_JOBS_FILE = "seen_jobs.json"


def _now():
    return datetime.now(timezone.utc).isoformat()


def load_state():
    if os.path.exists(SEEN_JOBS_FILE):
        try:
            with open(SEEN_JOBS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):  # migration ancien format (liste d'URLs)
                return {u: {"notified_at": "legacy"} for u in data}
            return data
        except Exception as e:
            print(f"Lecture {SEEN_JOBS_FILE} KO : {e}")
            return {}
    return {}


def save_state(state):
    try:
        with open(SEEN_JOBS_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=1)
    except Exception as e:
        print(f"Sauvegarde {SEEN_JOBS_FILE} KO : {e}")


def was_notified(offer_id, state):
    return offer_id in state and state[offer_id].get("notified_at")


def record_seen(job, state):
    oid = job.get("offer_id")
    if oid and oid not in state:
        state[oid] = {
            "first_seen": _now(),
            "published_at": job.get("published_at", ""),
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "notified_at": None,
        }


def mark_notified(offer_id, state):
    if offer_id in state:
        state[offer_id]["notified_at"] = _now()
