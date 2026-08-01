"""
Scoring par regles, 100% local (sans IA, sans cle API).
Renvoie un dict compatible avec utils/telegram.py.
"""
from datetime import datetime, timezone
from config.settings import (
    TARGET_KEYWORDS, EXCLUDED_KEYWORDS, ACCEPTED_LOCATIONS,
    ALLOWED_MAROC_COMPANIES, MAROC_TOP_TIER_ONLY,
    START_MONTH_PENALTIES, MIN_SCORE_THRESHOLD,
)

# Mots-cles a fort signal (coeur de cible d'Hatim)
STRONG = {
    "m&a", "mergers and acquisitions", "transaction services",
    "financial due diligence", "valuation", "evaluations", "corporate finance",
    "private equity", "deal advisory", "investment banking", "lbo", "restructuring",
}


def _text(job):
    return f"{job.get('title', '')} {job.get('description', '')}".lower()


def _is_stage(t):
    return any(k in t for k in ("stage", "stagiaire", "intern", "internship", "pfe"))


def _location_ok(job):
    loc = (job.get("location", "") or "").lower()
    if not loc:
        return True  # localisation inconnue -> on garde par precaution
    if any(a in loc for a in ACCEPTED_LOCATIONS):
        return True
    if any(m in loc for m in ("maroc", "morocco", "casablanca", "rabat")):
        if MAROC_TOP_TIER_ONLY:
            comp = (job.get("company", "") or "").lower()
            return any(m in comp for m in ALLOWED_MAROC_COMPANIES)
        return True
    return False


def _freshness_days(job):
    v = job.get("published_at")
    if not v:
        return None
    try:
        if isinstance(v, (int, float)) or (isinstance(v, str) and v.isdigit()):
            ts = float(v)
            if ts > 1e12:
                ts /= 1000.0
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        else:
            s = str(v).replace("Z", "+00:00")
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).days
    except Exception:
        return None


def evaluate_job(job):
    t = _text(job)

    # --- Rejets durs ---
    if not _is_stage(t):
        return {"match_score": 0, "rejected": True, "reason": "Pas un stage"}
    for k in EXCLUDED_KEYWORDS:
        if k in t:
            return {"match_score": 0, "rejected": True, "reason": f"Exclu ({k})"}
    if not _location_ok(job):
        return {"match_score": 0, "rejected": True, "reason": "Hors zone geographique"}

    # --- Fraicheur : au-dela de 7 jours = rejete ---
    days = _freshness_days(job)
    if days is not None and days > 7:
        return {"match_score": 0, "rejected": True, "reason": f"Offre trop ancienne ({days} j)"}

    # --- Score par mots-cles ---
    title = (job.get("title", "") or "").lower()
    desc = (job.get("description", "") or "").lower()
    score = 0
    matched = []
    for kw in TARGET_KEYWORDS:
        if kw in title:
            score += 50 if kw in STRONG else 28
            matched.append(kw)
        elif kw in desc:
            score += 14 if kw in STRONG else 7
            matched.append(kw)
    if not matched:
        return {"match_score": 0, "rejected": True, "reason": "Aucun mot-cle finance"}

    # --- Penalite selon le mois de demarrage detecte (le pire) ---
    penalties = [p for m, p in START_MONTH_PENALTIES.items() if m in t]
    mult = min(penalties) if penalties else 1.0

    # --- Bonus fraicheur ---
    boost = 0
    if days is not None:
        if days <= 0:
            boost = 12   # publie aujourd'hui
        elif days <= 1:
            boost = 6

    score = int(min(100, round(score * mult + boost)))
    matched = list(dict.fromkeys(matched))[:6]
    today = (days is not None and days <= 0)

    return {
        "match_score": score,
        "rejected": score < MIN_SCORE_THRESHOLD,
        "reason": "Score sous le seuil" if score < MIN_SCORE_THRESHOLD else "",
        "matched_terms": matched,
        "summary": ("Offre PUBLIEE AUJOURD'HUI, " if today else "Offre ") +
                   f"detectee directement sur le site de l'entreprise (source : {job.get('source', '')}).",
        "pros": "Correspond a ton profil sur : " + ", ".join(matched) + ".",
        "cons": "A verifier dans l'annonce : date de debut exacte et prerequis.",
        "pitch": "",
    }
