"""
Configuration globale et règles métier du Job Hunter.
"""

# Types de contrats acceptés
ACCEPTED_CONTRACTS = ["stage", "pfe", "end-of-study", "internship", "6 mois"]
REJECTED_CONTRACTS = ["alternance", "apprentissage", "contrat pro", "cdi", "cdd", "temps partiel", "stage court", "3 mois", "2 mois"]

# Zones géographiques acceptées
ACCEPTED_LOCATIONS = [
    "france", "paris", "île-de-france", "lyon", "bordeaux", "lille", "marseille", "toulouse",
    "luxembourg", "belgique", "bruxelles", "suisse", "genève", "zurich", "londres", "london", "uk"
]

# Règle d'exception pour le Maroc : uniquement entreprises de très grand prestige
MAROC_TOP_TIER_ONLY = True
ALLOWED_MAROC_COMPANIES = [
    "pwc", "kpmg", "ey", "deloitte", "lazard", "rothschild", "bnp paribas", "societe generale",
    "attijariwafa", "cdg", "bmce", "wavemaker", "bcg", "mckinsey", "bain"
]

# Intitulés cibles (Finance de haut de bilan & Direction Financière)
TARGET_KEYWORDS = [
    "transaction services", "financial due diligence", "ts", "m&a", "mergers and acquisitions",
    "investment banking", "private equity", "private debt", "valuation", "évaluations",
    "corporate finance", "corporate development", "restructuring", "deal advisory",
    "fp&a", "financial planning", "contrôle de gestion", "financial analyst",
    "analyste financier", "structuring", "leveraged finance", "lbo", "ecm", "dcm",
    "project finance", "working capital", "cash management", "business planning", "financial modeling"
]

# Intitulés strictement rejetés (Élimination automatique sans appel IA)
EXCLUDED_KEYWORDS = [
    "audit légal", "audit statutaire", "cac", "commissariat aux comptes",
    "comptabilité générale", "assistant comptable", "comptable unique", "comptable fournisseurs",
    "conseiller clientèle", "chargé d'accueil", "back office", "middle office reglementaire",
    "compliance", "kyc", "aml", "conformité", "business analyst tech", "actuariat",
    "data analyst", "développeur", "saisie comptable"
]

# Gestion de la période de démarrage
START_MONTH_PENALTIES = {
    "janvier": 1.0,    # Priorité max (100% de la note)
    "january": 1.0,
    "février": 0.95,   # Très bon (95%)
    "february": 0.95,
    "mars": 0.80,      # Pénalisé (80%)
    "march": 0.80,
    "avril": 0.40,     # Fortement pénalisé
    "april": 0.40,
    "mai": 0.20,
    "may": 0.20
}

# Seuil de score minimal pour envoi sur Telegram (en %)
MIN_SCORE_THRESHOLD = 60
