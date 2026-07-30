"""
Registre central des entreprises cibles (companies.csv).

Rôle :
- Charger la watchlist (1140+ boîtes finance) en mémoire.
- Faire correspondre le nom d'entreprise d'une offre à une cible (matching normalisé).
- Fournir le tier / score pour le boost de scoring.
- AUTO-DÉCOUVERTE : ajouter automatiquement à companies.csv toute nouvelle
  boîte finance croisée par les scrapers (tier "Découverte"), pour que la
  watchlist grossisse chaque jour.
"""

import csv
import os
import re
import unicodedata
from datetime import datetime

COMPANIES_FILE = "companies.csv"
FIELDNAMES = ["name", "category", "tier", "score_excel", "ats", "slug", "careers_url"]

# Tiers -> score de référence (utilisé pour le boost IA)
TIER_SCORE = {"Élite": 90, "Cible": 75, "Autre": 55, "Découverte": 65}

# Mots-clés qui identifient une boîte finance (sanity-check de l'auto-découverte)
FINANCE_HINTS = [
    "finance", "capital", "partners", "advisory", "advisors", "conseil", "corporate",
    "invest", "equity", "gestion", "asset", "management", "ventures", "venture",
    "m&a", "transaction", "valuation", "évaluation", "restructuring", "banque",
    "bank", "securities", "patrimoine", "croissance", "participations", "fund",
    "fonds", "développement", "transmission", "fusac", "fusions", "acquisitions",
    "wealth", "private", "debt", "midcap", "financial", "financière", "financiere",
]

# Termes qui disqualifient une "découverte" (bruit fréquent des agrégateurs)
DISCOVERY_BLACKLIST = [
    "linkedin", "voir détails", "voir details", "recruteur", "indeed", "welcome to",
    "jobteaser", "glassdoor", "n/a", "entreprise", "confidentiel", "cabinet de recrutement",
    "apec", "pôle emploi", "pole emploi", "hellowork", "michael page", "hays", "robert walters",
    "fed finance", "page personnel", "randstad", "adecco", "manpower",
]


def normalize(name: str) -> str:
    """Normalise un nom pour comparaison robuste (sans accents, ni ponctuation).
    On NE supprime PAS de mots (ex: "Group") pour éviter les collisions génériques."""
    if not name:
        return ""
    n = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii").lower()
    n = re.sub(r"[^a-z0-9]+", " ", n).strip()
    return n


# Tokens trop génériques pour matcher seuls (évite les faux positifs)
GENERIC_TOKENS = {
    "partners", "capital", "finance", "conseil", "invest", "group", "groupe",
    "ventures", "venture", "advisory", "advisors", "associes", "gestion", "corporate",
    "management", "equity", "financial", "financiere", "france", "paris", "co",
    "company", "sa", "sas", "asset", "banque", "bank", "the", "and", "et",
}


def _is_subsequence(short_toks, long_toks) -> bool:
    """True si short_toks apparaît comme sous-séquence CONTIGUË de long_toks."""
    n, m = len(short_toks), len(long_toks)
    if n == 0 or n > m:
        return False
    for i in range(m - n + 1):
        if long_toks[i:i + n] == short_toks:
            return True
    return False


class CompanyRegistry:
    def __init__(self, path: str = COMPANIES_FILE):
        self.path = path
        self.rows = []          # liste de dicts
        self.by_norm = {}       # nom normalisé -> row
        self._load()

    def _load(self):
        if not os.path.exists(self.path):
            print(f"⚠️ {self.path} introuvable — watchlist vide.")
            return
        with open(self.path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                self.rows.append(row)
                self.by_norm[normalize(row.get("name", ""))] = row
        print(f"📇 Watchlist chargée : {len(self.rows)} entreprises.")

    def match(self, company_name: str) -> dict | None:
        """Retourne la fiche entreprise si le nom correspond à une cible, sinon None.

        Stratégie :
          1) égalité normalisée exacte,
          2) le nom de la watchlist apparaît comme séquence de tokens contiguë
             dans le nom scrapé (ex: "Lazard" dans "Lazard Frères Gestion"),
             sauf si c'est un token unique générique ("Partners", "Capital"...).
        """
        n = normalize(company_name)
        if not n:
            return None
        if n in self.by_norm:
            return self.by_norm[n]

        cand_toks = n.split()
        best = None
        best_len = 0
        for norm_name, row in self.by_norm.items():
            if not norm_name:
                continue
            reg_toks = norm_name.split()
            # ignorer les cibles réduites à un seul token générique
            if len(reg_toks) == 1 and reg_toks[0] in GENERIC_TOKENS:
                continue
            # un token unique doit faire au moins 3 caractères pour matcher
            if len(reg_toks) == 1 and len(reg_toks[0]) < 3:
                continue
            if _is_subsequence(reg_toks, cand_toks) or _is_subsequence(cand_toks, reg_toks):
                # on garde la correspondance la plus spécifique (la plus longue)
                if len(reg_toks) > best_len:
                    best, best_len = row, len(reg_toks)
        return best

    def is_target(self, company_name: str) -> bool:
        return self.match(company_name) is not None

    def tier_of(self, company_name: str) -> str | None:
        row = self.match(company_name)
        return row.get("tier") if row else None

    def score_of(self, company_name: str) -> int:
        row = self.match(company_name)
        if not row:
            return 0
        try:
            return int(row.get("score_excel") or TIER_SCORE.get(row.get("tier"), 0))
        except (ValueError, TypeError):
            return TIER_SCORE.get(row.get("tier"), 0)

    # ---------- AUTO-DÉCOUVERTE ----------
    def looks_like_finance(self, company_name: str) -> bool:
        low = company_name.lower()
        if any(bad in low for bad in DISCOVERY_BLACKLIST):
            return False
        if len(company_name.strip()) < 3:
            return False
        return any(hint in low for hint in FINANCE_HINTS)

    def discover(self, company_name: str) -> bool:
        """
        Ajoute une nouvelle boîte finance à la watchlist si elle est pertinente et
        absente. Retourne True si une ligne a été ajoutée (à committer ensuite).
        """
        if not company_name:
            return False
        if self.is_target(company_name):
            return False
        if not self.looks_like_finance(company_name):
            return False
        row = {
            "name": company_name.strip(),
            "category": "Découverte",
            "tier": "Découverte",
            "score_excel": TIER_SCORE["Découverte"],
            "ats": "",
            "slug": "",
            "careers_url": f"# découvert le {datetime.now().strftime('%Y-%m-%d')}",
        }
        self.rows.append(row)
        self.by_norm[normalize(company_name)] = row
        print(f"🌱 Nouvelle entreprise découverte et ajoutée : {company_name}")
        return True

    def save(self):
        """Réécrit companies.csv (utilisé après des découvertes)."""
        with open(self.path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDNAMES)
            w.writeheader()
            for row in self.rows:
                w.writerow({k: row.get(k, "") for k in FIELDNAMES})
        print(f"💾 Watchlist sauvegardée : {len(self.rows)} entreprises.")


# Singleton partagé par le pipeline
_registry = None


def get_registry() -> CompanyRegistry:
    global _registry
    if _registry is None:
        _registry = CompanyRegistry()
    return _registry
