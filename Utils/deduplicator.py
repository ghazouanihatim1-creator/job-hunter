"""
Gestion de la mémoire du bot pour éviter tout doublon et économiser les appels IA.
"""

import json
import os
import re

SEEN_JOBS_FILE = "seen_jobs.json"

def normalize_url(url: str) -> str:
    """Normalise une URL pour éviter les doublons dus aux paramètres de tracking (UTM, source, etc.)."""
    if not url:
        return ""
    # Suppression des paramètres de requête inutiles (ex: ?utm_source=...)
    clean_url = url.split("?")[0].split("#")[0].strip().lower()
    # Retrait du slash final s'il existe
    if clean_url.endswith("/"):
        clean_url = clean_url[:-1]
    return clean_url

def load_seen_jobs() -> set:
    """Charge l'historique des offres déjà traitées."""
    if os.path.exists(SEEN_JOBS_FILE):
        try:
            with open(SEEN_JOBS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data)
        except Exception as e:
            print(f"⚠️ Erreur lors de la lecture de {SEEN_JOBS_FILE}: {e}")
            return set()
    return set()

def save_seen_jobs(seen_set: set) -> None:
    """Sauvegarde l'historique mis à jour."""
    try:
        with open(SEEN_JOBS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(seen_set), f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde de {SEEN_JOBS_FILE}: {e}")

def is_already_seen(job_url: str, seen_set: set) -> bool:
    """Vérifie si une offre a déjà été analysée."""
    clean = normalize_url(job_url)
    return clean in seen_set

def mark_as_seen(job_url: str, seen_set: set) -> None:
    """Ajoute une offre à la mémoire."""
    clean = normalize_url(job_url)
    if clean:
        seen_set.add(clean)
