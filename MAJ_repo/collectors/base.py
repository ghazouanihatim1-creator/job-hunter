"""
Socle commun des collecteurs (sources d'offres) + schema d'offre normalise.
Chaque collecteur herite de Collector et implemente fetch() -> list[dict].

Offre normalisee = dict avec les cles :
  company, title, url, location, date, published_at, source, offer_id, description
"""
import re
import html
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; JobHunterBot/1.0)",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}


def http_get(url, params=None, timeout=15):
    """GET securise : renvoie la reponse si 200, sinon None (jamais d'exception)."""
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
        return r if r.status_code == 200 else None
    except Exception as e:
        print(f"   HTTP KO {url[:70]} : {e}")
        return None


def strip_html(text):
    """Retire les balises HTML et decode les entites."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def make_offer_id(source, slug, native_id, url=""):
    """Identifiant stable et unique d'une offre."""
    if native_id:
        return f"{source}:{slug}:{native_id}"
    return f"{source}:{url}"


class Collector:
    """Interface commune. Chaque source concrete definit ats_type et fetch()."""
    ats_type = "base"

    def __init__(self, companies):
        # companies = liste de lignes companies.csv ayant cet ats_type
        self.companies = companies

    def fetch(self):
        raise NotImplementedError("fetch() doit etre implemente par le collecteur.")
