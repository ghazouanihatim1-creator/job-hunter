"""
Moteur d'évaluation IA probabiliste de candidatures (Groq Cloud / Llama-3.3-70b).
"""

import json
import os
from groq import Groq
from config.resume import get_candidate_summary_text
from config.settings import (
    ACCEPTED_CONTRACTS, REJECTED_CONTRACTS, 
    ACCEPTED_LOCATIONS, MAROC_TOP_TIER_ONLY, ALLOWED_MAROC_COMPANIES,
    EXCLUDED_KEYWORDS, START_MONTH_PENALTIES
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def quick_filter_check(job: dict) -> tuple[bool, str]:
    """
    Filtre rapide déterministe (sans IA) pour éliminer immédiatement
    les offres hors sujet (Audit légal, Alternance, Stage court, etc.).
    """
    title = job.get("title", "").lower()
    description = job.get("description", "").lower()
    company = job.get("company", "").lower()
    location = job.get("location", "").lower()
    full_text = f"{title} {description}"

    # 1. Vérification des mots-clés strictement exclus
    for kw in EXCLUDED_KEYWORDS:
        if kw.lower() in full_text:
            return False, f"Mot-clé exclu détecté : {kw}"

    # 2. Vérification du type de contrat (Exclusion des alternances, CDD, stages courts)
    if any(r_contract in full_text for r_contract in REJECTED_CONTRACTS):
        # Vérifier si ce n'est pas sauvé par un mot-clé de PFE clair
        if not any(a_contract in full_text for a_contract in ACCEPTED_CONTRACTS):
            return False, "Type de contrat non compatible (Alternance, CDD ou Stage court)"

    # 3. Règle spécifique Maroc : Rejet sauf très grandes enseignes/banques
    if "maroc" in location or "morocco" in location or "casablanca" in location or "rabat" in location:
        if MAROC_TOP_TIER_ONLY:
            if not any(top_co in company for top_co in ALLOWED_MAROC_COMPANIES):
                return False, "Offre au Maroc hors entreprises du Top-Tier prédéfinies"

    return True, "Filtre rapide validé"


def evaluate_job_with_ai(job: dict) -> dict:
    """
    Évalue une offre via Groq et renvoie une analyse structurée probabiliste.
    """
    # Étape 1 : Passation du filtre déterministe
    passed, reason = quick_filter_check(job)
    if not passed:
        print(f"⏩ Offre ignorée ({reason}) : {job.get('title')}")
        return {"match_score": 0, "rejected": True, "reason": reason}

    # Étape 2 : Préparation du Prompt pour le LLM
    candidate_cv = get_candidate_summary_text()
    
    prompt = f"""
Tu es un Partner en Recrutement spécialisé dans la Finance d'Entreprise (M&A, Transaction Services, Private Equity, FP&A).
Ta mission est d'évaluer la PROBABILITÉ RÉELLE que ce candidat soit retenu pour un entretien pour cette offre.

--- PROFIL DU CANDIDAT ---
{candidate_cv}

--- OFFRE D'EMPLOI À ÉVALUER ---
Titre du poste : {job.get('title')}
Entreprise : {job.get('company')}
Localisation : {job.get('location')}
Période / Date : {job.get('date', 'Non précisée')}
Description :
{job.get('description', 'Pas de description détaillée disponible.')}

--- CONSIGNES D'ÉVALUATION ---
1. Rejette (score = 0) si l'offre concerne l'audit légal (CAC), la comptabilité générale, ou une alternance/apprentissage.
2. Tiens compte de la sélectivité de l'entreprise (ex: boutique M&A/PE de premier plan = sélectivité très haute, soit exigeant).
3. Tiens compte de la date de démarrage (Début Janvier = parfait. Février/Mars = pénalisé. Après Avril = rejeté).
4. Attribue un score de 0 à 100 qui représente la PROBABILITÉ RÉELLE DE DÉCROCHER UN ENTRETIEN (et non juste la ressemblance théorique).

--- FORMAT DE RÉPONSE EXIGÉ (JSON STRICT UNIQUEMENT) ---
{{
    "match_score": 85,
    "summary": "Résumé concis de l'offre en 2 phrases.",
    "pros": "2 ou 3 points forts clés du candidat pour cette offre.",
    "cons": "Points faibles ou éléments de vigilance (ex: sélectivité élevée, date tardive).",
    "pitch": "Un pitch d'accroche personnalisé de 2 phrases prêt à être envoyé au recruteur."
}}
"""

    if not GROQ_API_KEY:
        print("⚠️ GROQ_API_KEY non disponible. Scoring par défaut.")
        return {
            "match_score": 75,
            "summary": "Analyse automatique (Clé API Groq non configurée).",
            "pros": "Excellente adéquation avec les domaines cibles.",
            "cons": "Évaluation détaillée indisponible.",
            "pitch": f"Bonjour, fortement intéressé par le poste de {job.get('title')}, mon profil en finance d'entreprise correspond parfaitement à vos recherches."
        }

    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content.strip()
        result = json.loads(content)
        
        # Validation que le score est un entier
        result["match_score"] = int(result.get("match_score", 0))
        return result

    except Exception as e:
        print(f"❌ Erreur lors de l'évaluation Groq : {e}")
        return {
            "match_score": 65,
            "summary": f"Poste en finance chez {job.get('company')}.",
            "pros": "Correspondance sur les mots-clés principaux.",
            "cons": "Analyse IA incomplète.",
            "pitch": f"Bonjour, je postule à votre offre de {job.get('title')}. Mon parcours en finance d'entreprise s'aligne très bien avec vos attentes."
        }
