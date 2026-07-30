"""
Enrichissement de la base d'entreprises (companies.csv).

But : partir d'une liste de NOMS d'entreprises (issue de ton Excel) et trouver,
pour chacune, par quel canal la surveiller :
  1) un ATS officiel (Greenhouse / Lever / Ashby / SmartRecruiters)  -> statut="ats"
  2) sinon sa page carrière officielle                              -> statut="careers"
  3) sinon rien de fiable -> surveillée via agrégateurs + LinkedIn   -> statut="aggregateurs"

⚠️ À exécuter là où Internet est libre (GitHub Actions ou ta machine),
   PAS dans un environnement réseau restreint.

Le script est RÉ-ENTRANT : il ignore les lignes déjà enrichies (statut != "a_enrichir"),
donc tu peux le relancer sans tout recommencer. Il sauvegarde régulièrement.

Usage :
    python enrich_companies.py                # enrichit tout ce qui reste
    python enrich_companies.py --limit 50     # ne traite que 50 boîtes (test)
    python enrich_companies.py --force        # ré-enrichit tout depuis zéro
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import time
import unicodedata

import requests
from bs4 import BeautifulSoup

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "companies.csv")
FIELDS = ["name", "categorie", "tier", "score_excel", "ats", "slug", "careers_url", "statut"]

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
DELAY = 0.6          # pause entre requêtes (politesse + anti-blocage)
SAVE_EVERY = 25      # sauvegarde tous les N enrichissements


# --------------------------------------------------------------------- #
#  Génération des slugs candidats à partir d'un nom d'entreprise
# --------------------------------------------------------------------- #
def normalize(name: str) -> str:
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return s.lower().strip()

def candidate_slugs(name: str) -> list[str]:
    base = normalize(name)
    cands = []

    # 1) Nom COMPLET (prioritaire) : sans espace puis avec tirets
    full = re.sub(r"[^a-z0-9]+", " ", base).split()
    if full:
        for c in ("".join(full), "-".join(full)):
            if c and c not in cands:
                cands.append(c)

    # 2) Nom RACCOURCI : sans les suffixes juridiques/génériques courants
    stripped = re.sub(r"\b(sas|sa|sarl|group|groupe|partners|capital|finance|advisory)\b",
                      " ", base)
    short = re.sub(r"[^a-z0-9]+", " ", stripped).split()
    if short:
        for c in ("".join(short), "-".join(short)):
            if c and c not in cands:
                cands.append(c)

    return cands


# --------------------------------------------------------------------- #
#  Sondes ATS : renvoient True si un board valide existe pour ce slug
# --------------------------------------------------------------------- #
def _get(url):
    try:
        return requests.get(url, headers=UA, timeout=10)
    except Exception:
        return None

def probe_greenhouse(slug):
    r = _get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs")
    return bool(r and r.status_code == 200 and "jobs" in r.text)

def probe_lever(slug):
    r = _get(f"https://api.lever.co/v0/postings/{slug}?mode=json")
    return bool(r and r.status_code == 200 and r.text.strip().startswith("["))

def probe_ashby(slug):
    r = _get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}")
    return bool(r and r.status_code == 200 and "jobs" in r.text)

def probe_smartrecruiters(slug):
    r = _get(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=1")
    return bool(r and r.status_code == 200 and "content" in r.text)

PROBES = [("greenhouse", probe_greenhouse), ("lever", probe_lever),
          ("ashby", probe_ashby), ("smartrecruiters", probe_smartrecruiters)]

def detect_ats(name: str):
    """Retourne (ats, slug) si un board est trouvé, sinon (None, None)."""
    for slug in candidate_slugs(name):
        for ats_name, probe in PROBES:
            if probe(slug):
                return ats_name, slug
            time.sleep(DELAY)
    return None, None


# --------------------------------------------------------------------- #
#  Recherche de la page carrière via DuckDuckGo HTML (sans API)
# --------------------------------------------------------------------- #
CAREER_HINTS = ("career", "carriere", "carrieres", "recrutement", "jobs",
                "rejoignez", "nous-rejoindre", "join", "emploi")

def find_careers_page(name: str):
    q = f'"{name}" recrutement OR carrières OR careers'
    try:
        r = requests.get("https://html.duckduckgo.com/html/",
                         params={"q": q}, headers=UA, timeout=12)
        if r.status_code != 200:
            return ""
        soup = BeautifulSoup(r.text, "lxml")
        for a in soup.select("a.result__url, a.result__a"):
            href = a.get("href", "")
            if "uddg=" in href:
                import urllib.parse
                href = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
            low = href.lower()
            if any(h in low for h in CAREER_HINTS):
                return href
        return ""
    except Exception:
        return ""


# --------------------------------------------------------------------- #
#  Lecture / écriture de la base
# --------------------------------------------------------------------- #
def load_rows():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def save_rows(rows):
    tmp = CSV_PATH + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})
    os.replace(tmp, CSV_PATH)


# --------------------------------------------------------------------- #
#  Boucle principale
# --------------------------------------------------------------------- #
def run(limit=None, force=False):
    rows = load_rows()
    todo = [r for r in rows if force or r.get("statut", "") in ("", "a_enrichir")]
    if limit:
        todo = todo[:limit]
    print(f"🔎 {len(todo)} entreprise(s) à enrichir (sur {len(rows)} au total)")

    stats = {"ats": 0, "careers": 0, "aggregateurs": 0}
    done = 0
    for r in todo:
        name = r["name"]
        ats, slug = detect_ats(name)
        if ats:
            r["ats"], r["slug"], r["statut"] = ats, slug, "ats"
            stats["ats"] += 1
            print(f"  ✅ {name} -> {ats}:{slug}")
        else:
            url = find_careers_page(name)
            time.sleep(DELAY)
            if url:
                r["careers_url"], r["statut"] = url, "careers"
                stats["careers"] += 1
                print(f"  🌐 {name} -> page carrière")
            else:
                r["statut"] = "aggregateurs"
                stats["aggregateurs"] += 1
                print(f"  🔁 {name} -> agrégateurs/LinkedIn")

        done += 1
        if done % SAVE_EVERY == 0:
            save_rows(rows)
            print(f"  💾 sauvegarde intermédiaire ({done}/{len(todo)})")

    save_rows(rows)
    print(f"\n✅ Terminé. ATS: {stats['ats']} | Pages carrière: {stats['careers']} | "
          f"Agrégateurs: {stats['aggregateurs']}")


def main():
    p = argparse.ArgumentParser(description="Enrichissement companies.csv")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--force", action="store_true")
    args = p.parse_args()
    run(limit=args.limit, force=args.force)


if __name__ == "__main__":
    main()
