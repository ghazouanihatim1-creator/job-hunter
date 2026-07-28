"""
Classe de base abstraite et utilitaires pour l'ensemble des scrapers.
"""

import requests
import random
import time

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
]

class BaseScraper:
    def __init__(self, name: str):
        self.name = name

    def get_headers(self) -> dict:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    def safe_get(self, url: str, params: dict = None, json_body: dict = None, timeout: int = 10) -> requests.Response:
        """Effectue une requête HTTP sécurisée avec gestion des retards."""
        try:
            time.sleep(random.uniform(0.5, 1.5))
            if json_body:
                response = requests.post(url, json=json_body, headers=self.get_headers(), timeout=timeout)
            else:
                response = requests.get(url, params=params, headers=self.get_headers(), timeout=timeout)
            return response
        except Exception as e:
            print(f"⚠️ Erreur HTTP dans {self.name} pour URL {url} : {e}")
            return None

    def fetch_jobs((self) -> list[dict]:
        """Méthode à surcharger par chaque scraper spécifique."""
        raise NotImplementedError("La méthode fetch_jobs doit être implémentée.")
