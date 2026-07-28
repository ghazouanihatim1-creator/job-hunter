"""
Classe de base abstraite et filtres de qualité stricts (Règle des 7 jours max).
"""

import requests
import random
import time
from datetime import datetime, timedelta

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

EXCLUDED_KEYWORDS = [
    "avocat", "juriste", "legal", "lawyer", "droit", "juridique",
    "alternance", "apprentissage", "cdi", "cdd"
]

class BaseScraper:
    def __init__(self, name: str):
        self.name = name

    def get_headers(self) -> dict:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    def safe_get(self, url: str, params: dict = None, json_body: dict = None, timeout: int = 10) -> requests.Response:
        try:
            time.sleep(random.uniform(0.5, 1.2))
            if json_body:
                response = requests.post(url, json=json_body, headers=self.get_headers(), timeout=timeout)
            else:
                response = requests.get(url, params=params, headers=self.get_headers(), timeout=timeout)
            return response
        except Exception as e:
            print(f"⚠️ Erreur HTTP dans {self.name} : {e}")
            return None

    def is_within_7_days(self, date_str: str) -> bool:
        """Vérifie si la date de publication est inférieure ou égale à 7 jours."""
        if not date_str or date_str == "Récemment":
            return True  # On conserve par précaution si la date précise n'est pas fournie

        try:
            # Nettoyage et conversion de la date
            now = datetime.now()
            # Format courant type "Wed, 22 Jul 2026"
            pub_date = datetime.strptime(date_str[:16], "%a, %d %b %Y")
            diff_days = (now - pub_date).days
            return diff_days <= 7
        except Exception:
            return True

    def is_valid_job(self, title: str, description: str, date_str: str = "") -> bool:
        """Filtre global : Mots-clés + Fraîcheur des 7 jours."""
        full_text = f"{title} {description}".lower()

        # 1. Exclusion mots-clés
        for keyword in EXCLUDED_KEYWORDS:
            if keyword in full_text:
                return False

        # 2. Exigence du terme 'stage' / 'intern'
        if "stage" not in full_text and "intern" not in full_text and "internship" not in full_text:
            return False

        # 3. Filtre strict de 7 jours max
        if not self.is_within_7_days(date_str):
            print(f"⌛ Offre rejetée (plus de 7 jours) : {title} ({date_str})")
            return False

        return True

    def fetch_jobs(self) -> list[dict]:
        raise NotImplementedError("La méthode fetch_jobs doit être implémentée.")
