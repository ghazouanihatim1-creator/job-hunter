"""
Enrichissement de companies.csv : détecte l'ATS de chaque entreprise.

Pour chaque boîte sans ATS renseigné, on devine un slug à partir du nom et on
teste les boards publics (Greenhouse, Lever, Ashby, SmartRecruiters). Si l'un
répond, on écrit `ats` + `slug`. Ré-entrant : sauvegarde en continu, reprend où
il s'est arrêté. Doit tourner sur GitHub Actions (réseau requis).
"""

import csv
import re
import time
import unicodedata
import requests

COMPANIES_FILE = "companies.csv"
FIELDNAMES = ["name", "category", "tier", "score_excel", "ats", "slug", "careers_url"]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JobHunterBot/1.0)"}
TIMEOUT = 8


def slugify(name: str) -> str:
    n = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii").lower()
    n = re.sub(r"\b(sa|sas|sarl|llc|ltd|inc|gmbh|group|groupe|france|paris)\b", "", n)
    n = re.sub(r"[^a-z0-9]+", "", n).strip()
    return n


def probe(url: str) -> bool:
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code != 200:
            return False
        # board vide mais valide = quand même un ATS détecté
        return True
    except Exception:
        return False


def detect_ats(slug: str):
    candidates = [
        ("greenhouse", f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"),
        ("lever", f"https://api.lever.co/v0/postings/{slug}?mode=json"),
        ("ashby", f"https://api.ashbyhq.com/posting-api/job-board/{slug}"),
        ("smartrecruiters", f"https://api.smartrecruiters.com/v1/companies/{slug}/postings"),
    ]
    for ats, url in candidates:
        if probe(url):
            return ats
        time.sleep(0.3)
    return None


def load_rows():
    with open(COMPANIES_FILE, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_rows(rows):
    with open(COMPANIES_FILE, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDNAMES})


def main():
    rows = load_rows()
    total = len(rows)
    todo = [r for r in rows if not r.get("ats")]
    print(f"📇 {total} entreprises, {len(todo)} à enrichir.")

    detected = 0
    for i, row in enumerate(todo, start=1):
        slug = slugify(row["name"])
        if not slug:
            row["ats"] = "-"  # marque comme traité
            continue
        ats = detect_ats(slug)
        if ats:
            row["ats"] = ats
            row["slug"] = slug
            detected += 1
            print(f"  ✅ {row['name']} -> {ats} ({slug})")
        else:
            row["ats"] = "-"  # aucun ATS ; évite de re-tester au prochain run

        if i % 25 == 0:
            save_rows(rows)
            print(f"  ... {i}/{len(todo)} traités, {detected} ATS détectés (sauvegarde).")

    save_rows(rows)
    print(f"🏁 Terminé : {detected} ATS détectés sur {len(todo)} testés.")


if __name__ == "__main__":
    main()
