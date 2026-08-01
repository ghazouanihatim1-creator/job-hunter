"""
Resolveur ATS : pour chaque entreprise sans ats_type, teste des slugs candidats
contre Greenhouse, Lever et SmartRecruiters (APIs publiques, sans cle).
Remplit ats_type + ats_slug dans companies.csv. Reprend la ou il s'est arrete
(les lignes deja resolues sont ignorees).

Lancement : onglet Actions -> "Resolveur ATS" -> Run workflow.
"""
import csv
import re
import time
import unicodedata
import requests

CSV_FILE = "companies.csv"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JobHunterBot/1.0)"}
PAUSE = 0.25  # secondes entre requetes (politesse / anti-blocage)


def slug_variants(name):
    s = unicodedata.normalize("NFD", name)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    words = [w for w in s.split() if w not in ("sa", "sas", "sarl", "group", "groupe", "the")]
    if not words:
        return []
    cands = []
    for v in ("".join(words), "-".join(words), "".join(words[:2]), words[0]):
        if len(v) >= 3 and v not in cands:
            cands.append(v)
    return cands


def _ok(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        return r.status_code == 200, r
    except Exception:
        return False, None


def try_greenhouse(slug):
    ok, r = _ok(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs")
    if ok:
        try:
            return r.json().get("jobs") is not None
        except Exception:
            return False
    return False


def try_lever(slug):
    ok, r = _ok(f"https://api.lever.co/v0/postings/{slug}?mode=json")
    if ok:
        try:
            return isinstance(r.json(), list)
        except Exception:
            return False
    return False


def try_smartrecruiters(slug):
    ok, r = _ok(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=1")
    if ok:
        try:
            return "content" in r.json()
        except Exception:
            return False
    return False


ATS_TESTS = [("greenhouse", try_greenhouse), ("lever", try_lever),
             ("smartrecruiters", try_smartrecruiters)]


def resolve():
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        fields = rows[0].keys() if rows else []

    todo = [r for r in rows if not (r.get("ats_type") or "").strip()]
    print(f"{len(rows)} entreprises | {len(todo)} a resoudre")

    found = 0
    for i, row in enumerate(todo, 1):
        name = row.get("name", "")
        hit = False
        for slug in slug_variants(name):
            for ats_name, test in ATS_TESTS:
                try:
                    if test(slug):
                        row["ats_type"] = ats_name
                        row["ats_slug"] = slug
                        found += 1
                        hit = True
                        print(f"  OK {name} -> {ats_name}:{slug}")
                        break
                except Exception:
                    pass
                time.sleep(PAUSE)
            if hit:
                break
        # Sauvegarde reguliere pour ne rien perdre en cas d'arret
        if i % 50 == 0:
            _save(rows, fields)
            print(f"  ... {i}/{len(todo)} ({found} trouves)")

    _save(rows, fields)
    print(f"TERMINE : {found} entreprises rattachees a un ATS.")


def _save(rows, fields):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(fields))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    resolve()
