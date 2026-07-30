"""
Moteur d'évaluation IA (Groq / Llama-3.3-70b) + boost selon le tier de l'entreprise.
"""

import os
import json
from groq import Groq
from config.resume import get_candidate_summary_text

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.3-70b-versatile"

# Bonus de score selon le prestige de l'entreprise (issu de la watchlist)
TIER_BOOST = {"Élite": 12, "Cible": 6, "Autre": 2, "Découverte": 3}


def evaluate_job_with_ai(job: dict) -> dict:
    if not GROQ_API_KEY:
        return {"match_score": 0, "summary": "Clé API manquante", "pros": "", "cons": "", "pitch": ""}

    client = Groq(api_key=GROQ_API_KEY)
    candidate_profile = get_candidate_summary_text()

    prompt = f"""
Tu es un Chasseur de Têtes Senior spécialisé en Finance d'Entreprise (M&A, TS, FP&A, Corporate Finance).
Évalue l'adéquation exacte entre l'offre d'emploi suivante et le profil du candidat.

--- PROFIL DU CANDIDAT ---
{candidate_profile}

--- OFFRE D'EMPLOI À ÉVALUER ---
Titre : {job.get('title')}
Entreprise : {job.get('company')}
Description : {job.get('description')}
Date publication / Détails : {job.get('date')}

--- RÈGLES D'ÉVALUATION STRICTES ---
1. Si l'offre requiert un diplôme en DROIT, un profil JURIDIQUE ou AVOCAT -> score 0.
2. Si le démarrage est incompatible avec les disponibilités (le candidat vise janvier 2027,
   ok février/mars) -> réduis le score de 30 points.
3. Rédige un JSON strict sans texte autour avec les clés :
   - "match_score": entier 0-100
   - "summary": résumé de l'offre en 2 phrases
   - "pros": 2 points forts majeurs
   - "cons": points de vigilance
   - "pitch": accroche percutante en 2-3 phrases pour le recruteur

Retourne UNIQUEMENT le JSON.
"""

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"❌ Erreur évaluation Groq : {e}")
        return {"match_score": 0, "summary": "Erreur d'analyse", "pros": "", "cons": "", "pitch": ""}


def apply_tier_boost(analysis: dict, tier: str | None) -> dict:
    """Ajoute un bonus de score selon le tier de l'entreprise (plafonné à 100)."""
    if not tier:
        return analysis
    boost = TIER_BOOST.get(tier, 0)
    base = analysis.get("match_score", 0) or 0
    if base > 0:  # ne booste pas une offre disqualifiée (score 0)
        analysis["match_score"] = min(100, base + boost)
        analysis["tier"] = tier
    return analysis
