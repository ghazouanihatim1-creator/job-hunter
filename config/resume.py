"""
Profil candidat structuré pour le moteur d'évaluation IA (Groq/Llama-3.3).
"""

CANDIDATE_PROFILE = {
    "target_role": "Stage de fin d'études (PFE) / 6 mois en M&A, Transaction Services, FP&A ou Corporate Finance.",
    "career_path": "Transaction Services -> M&A -> Investment Banking -> Private Equity",

    "education": {
        "level": "Master 2 / Grande École de Commerce ou Master Finance",
        "majors": ["Finance d'Entreprise", "Corporate Finance", "Ingénierie Financière"],
        "key_courses": ["Analyse financière avancée", "Modélisation LBO/M&A",
                        "Évaluation d'entreprises (DCF, Multiples)", "Comptabilité IFRS / US GAAP"],
    },

    "experience_summary": [
        "Stages précédents en finance d'entreprise / analyse financière / audit / contrôle de gestion.",
        "Pratique de la modélisation sous Excel (P&L, Bilan, Tableau de Flux de Trésorerie).",
        "Analyse de la performance financière et revue de Business Plans.",
    ],

    "technical_skills": [
        "Modélisation financière (Financial Modeling & Valuation)",
        "Méthodes d'évaluation : DCF, Comparables boursiers, Transactions précédentes",
        "Analyse des états financiers & Normes comptables",
        "Maîtrise avancée d'Excel (Fonctions complexes, Modélisation), PowerPoint",
        "Recherche d'information financière (Capital IQ, Bloomberg, FactSet - notion/pratique)",
    ],

    "languages": {
        "french": "Maternelle / Courant (Rédaction parfaite)",
        "english": "Professionnel / Avancé (Capacité à travailler et analyser des memos en anglais)",
    },

    "availability": "Recherche prioritaire : Début Janvier 2027 (ou Février / Mars maximum).",
}


def get_candidate_summary_text() -> str:
    """Convertit le profil structuré en un bloc texte optimisé pour le prompt LLM."""
    exp_str = "\n- ".join(CANDIDATE_PROFILE["experience_summary"])
    skills_str = "\n- ".join(CANDIDATE_PROFILE["technical_skills"])
    majors_str = ", ".join(CANDIDATE_PROFILE["education"]["majors"])
    courses_str = ", ".join(CANDIDATE_PROFILE["education"]["key_courses"])

    return f"""
Objectif : {CANDIDATE_PROFILE['target_role']}
Trajectoire visée : {CANDIDATE_PROFILE['career_path']}

Formation : {CANDIDATE_PROFILE['education']['level']} ({majors_str})
Cours clés : {courses_str}

Expériences :
- {exp_str}

Compétences Techniques :
- {skills_str}

Langues : Français ({CANDIDATE_PROFILE['languages']['french']}) | Anglais ({CANDIDATE_PROFILE['languages']['english']})
Disponibilité : {CANDIDATE_PROFILE['availability']}
"""
