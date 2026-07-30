"""
Configuration globale et règles métier du Job Hunter.
"""

# Types de contrats acceptés / rejetés
ACCEPTED_CONTRACTS = ["stage", "stagiaire", "pfe", "fin d'études", "internship", "intern", "6 mois"]
REJECTED_CONTRACTS = ["alternance", "apprentissage", "contrat pro", "cdi", "cdd",
                      "temps partiel", "stage court", "3 mois", "2 mois", "v.i.e", "vie"]

# Zones géographiques acceptées (Europe + Maroc si prestige)
ACCEPTED_LOCATIONS = [
    "france", "paris", "île-de-france", "ile-de-france", "lyon", "bordeaux", "lille",
    "marseille", "toulouse", "nantes", "luxembourg", "belgique", "bruxelles", "belgium",
    "suisse", "genève", "geneva", "zurich", "londres", "london", "uk", "amsterdam",
    "francfort", "frankfurt", "madrid", "milan", "maroc", "casablanca", "rabat",
]

# Maroc : uniquement maisons très prestigieuses
MAROC_TOP_TIER_ONLY = True
ALLOWED_MAROC_COMPANIES = [
    "pwc", "kpmg", "ey", "deloitte", "lazard", "rothschild", "bnp paribas", "societe generale",
    "attijariwafa", "attijari", "cdg", "bmce", "bcg", "mckinsey", "bain", "red med", "upline",
]

# Intitulés cibles (finance haut de bilan & direction financière) — en minuscules
TARGET_KEYWORDS = [
    "transaction services", "financial due diligence", "due diligence", "m&a",
    "mergers and acquisitions", "mergers & acquisitions", "fusions", "acquisitions",
    "investment banking", "private equity", "private debt", "venture capital",
    "valuation", "évaluation", "evaluation", "corporate finance", "corporate development",
    "restructuring", "deal advisory", "fp&a", "financial planning", "contrôle de gestion",
    "financial analyst", "analyste financier", "structuring", "leveraged finance", "lbo",
    "ecm", "dcm", "project finance", "debt advisory", "financial modeling", "modélisation",
    "capital markets", "growth equity", "asset management", "infrastructure",
]

# Intitulés strictement rejetés (élimination automatique sans appel IA)
EXCLUDED_KEYWORDS = [
    "audit légal", "audit statutaire", "commissariat aux comptes",
    "comptabilité générale", "assistant comptable", "comptable unique", "comptable fournisseurs",
    "conseiller clientèle", "chargé d'accueil", "back office", "middle office reglementaire",
    "compliance", "kyc", "aml", "conformité", "business analyst tech", "actuariat",
    "data analyst", "développeur", "developer", "saisie comptable", "juridique", "avocat",
]

# Pénalités selon le mois de démarrage (janvier 2027 prioritaire)
START_MONTH_PENALTIES = {
    "janvier": 1.0, "january": 1.0,
    "février": 0.95, "fevrier": 0.95, "february": 0.95,
    "mars": 0.80, "march": 0.80,
    "avril": 0.40, "april": 0.40,
    "mai": 0.20, "may": 0.20,
}

# Seuil de score minimal pour alerte Telegram (en %)
MIN_SCORE_THRESHOLD = 60

# Auto-découverte : ajouter à la watchlist les nouvelles boîtes finance croisées
ENABLE_DISCOVERY = True
