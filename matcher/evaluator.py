"""
Moteur d'évaluation IA ajusté pour sanctionner les profils juridiques ou hors délais.
"""

import os
import json
from groq import Groq
from config.resume import get_candidate_summary_text
from config.settings import MIN_SCORE_THRESHOLD

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

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
1. Si l'offre requiert un diplôme en DROIT, un profil JURIDIQUE ou AVOCAT -> Attribue un score de 0%.
2. Si le démarrage de l'offre est incompatible avec les disponibilités du candidat (ex: Mi-2026 alors qu'il veut Janvier 2027) -> Réduis le score de 30 points.
3. Rédige un JSON strict sans texte autour avec les clés suivantes :
   - "match_score": entier entre 0 et 100
   - "summary": court résumé de l'offre en 2 phrases
   - "pros": 2 points forts majeurs
   - "cons": points de vigilance ou limites de la candidature
   - "pitch": accroche percutante en 2-3 phrases pour l'accroche recruteur

Retourne UNIQUEMENT le JSON.
"""

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"❌ Erreur évaluation Groq : {e}")
        return {"match_score": 0, "summary": "Erreur d'analyse", "pros": "", "cons": "", "pitch": ""}
