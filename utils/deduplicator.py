"""
Mémoire anti-doublon du bot (seen_jobs.json) pour éviter de re-alerter et
d'appeler l'IA inutilement.
"""

import json
import os

SEEN_JOBS_FILE = "seen_jobs.json"


def normalize_url(url: str) -> str:
    """Normalise une URL (retire tracking, ancre, slash final)."""
    if not url:
        return ""
    clean = url.split("?")[0].split("#")[0].strip().lower()
    return clean[:-1] if clean.endswith("/") else clean


def load_seen_jobs() -> set:
    if os.path.exists(SEEN_JOBS_FILE):
        try:
            with open(SEEN_JOBS_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            print(f"⚠️ Lecture {SEEN_JOBS_FILE} : {e}")
            return set()
    return set()


def save_seen_jobs(seen_set: set) -> None:
    try:
        with open(SEEN_JOBS_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(seen_set), f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Sauvegarde {SEEN_JOBS_FILE} : {e}")


def is_already_seen(job_url: str, seen_set: set) -> bool:
    return normalize_url(job_url) in seen_set


def mark_as_seen(job_url: str, seen_set: set) -> None:
    clean = normalize_url(job_url)
    if clean:
        seen_set.add(clean)
