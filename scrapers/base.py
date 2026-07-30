"""
Classe de base abstraite et filtres de qualité (fraîcheur 7 jours, stage/PFE).

Correctifs vs version initiale :
- Le filtre acceptait uniquement le mot "stage"/"intern" et rejetait à tort
  "Stagiaire M&A", "PFE", "fin d'études". Corrigé (STAGE_TERMS élargi).
- Exclusion des vrais contrats non désirés (alternance, CDI...) conservée.
"""

import requests
import random
import time
from datetime import datetime

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]

# Termes qui indiquent un stage / PFE (au moins un requis)
STAGE_TERMS = [
    "stage", "stagiaire", "pfe", "fin d'études", "fin d'etudes", "fin d’études",
    "intern", "internship", "trainee", "graduate programme", "graduate program",
    "summer analyst", "off-cycle", "off cycle", "end of study", "6 mois", "6-month",
]

# Termes strictement exclus (élimination sans appel IA)
EXCLUDED_KEYWORDS = [
    "avocat", "juriste", "legal counsel", "lawyer", "droit ", "juridique",
    "alternance", "apprentissage", "apprenti", "contrat pro", "professionnalisation",
    "cdi ", "cdd ", "temps partiel", "vie ", "v.i.e", "volontariat",
]


class BaseScraper:
    def __init__(self, name: str):
        self.name = name

    def get_headers(self) -> dict:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    def safe_get(self, url: str, params: dict = None, json_body: dict = None, timeout: int = 12):
        try:
            time.sleep(random.uniform(0.5, 1.2))
            if json_body:
                return requests.post(url, json=json_body, headers=self.get_headers(), timeout=timeout)
            return requests.get(url, params=params, headers=self.get_headers(), timeout=timeout)
        except Exception as e:
            print(f"⚠️ Erreur HTTP dans {self.name} : {e}")
            return None

    def is_within_7_days(self, date_str: str) -> bool:
        """True si la publication date de 7 jours ou moins (ou si date inconnue)."""
        if not date_str or date_str in ("Récemment", "Recently"):
            return True
        for fmt in ("%a, %d %b %Y", "%Y-%m-%d", "%d/%m/%Y"):
            try:
                pub = datetime.strptime(date_str[:len(datetime.now().strftime(fmt))], fmt)
                return (datetime.now() - pub).days <= 7
            except Exception:
                continue
        return True  # par précaution si le format est inconnu

    def is_stage(self, text: str) -> bool:
        low = text.lower()
        return any(term in low for term in STAGE_TERMS)

    def is_excluded(self, text: str) -> bool:
        low = f" {text.lower()} "
        return any(bad in low for bad in EXCLUDED_KEYWORDS)

    def is_valid_job(self, title: str, description: str = "", date_str: str = "") -> bool:
        """Filtre global : stage/PFE requis, exclusions, fraîcheur 7 jours."""
        full_text = f"{title} {description}"

        if self.is_excluded(full_text):
            return False

        if not self.is_stage(full_text):
            return False

        if not self.is_within_7_days(date_str):
            print(f"⌛ Rejetée (> 7 jours) : {title} ({date_str})")
            return False

        return True

    def fetch_jobs(self) -> list:
        raise NotImplementedError("fetch_jobs doit être implémentée.")
