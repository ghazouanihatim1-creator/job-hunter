"""
Configuration globale et regles metier du Job Hunter.
"""

# Types de contrats acceptes
ACCEPTED_CONTRACTS = ["stage", "pfe", "end-of-study", "internship", "6 mois"]
REJECTED_CONTRACTS = ["alternance", "apprentissage", "contrat pro", "cdi", "cdd",
                      "temps partiel", "stage court", "3 mois", "2 mois"]

# Zones geographiques acceptees (France + Europe/International)
ACCEPTED_LOCATIONS = [
    "france", "paris", "ile-de-france", "lyon", "bordeaux", "lille", "marseille",
    "toulouse", "nantes", "clermont", "luxembourg", "belgique", "bruxelles", "brussels",
    "suisse", "switzerland", "geneve", "geneva", "zurich", "londres", "london", "uk",
    "united kingdom", "amsterdam", "madrid", "milan", "milano", "frankfurt", "dublin",
    "remote", "hybrid", "hybride", "europe",
]

# Exception Maroc : uniquement entreprises de tres grand prestige
MAROC_TOP_TIER_ONLY = True
ALLOWED_MAROC_COMPANIES = [
    "pwc", "kpmg", "ey", "deloitte", "lazard", "rothschild", "bnp paribas",
    "societe generale", "attijari", "cdg", "bmce", "bcg", "mckinsey", "bain",
]

# Intitules cibles (Finance de haut de bilan & Direction Financiere)
TARGET_KEYWORDS = [
    "transaction services", "financial due diligence", "due diligence", "m&a",
    "mergers and acquisitions", "mergers", "acquisitions", "investment banking",
    "private equity", "private debt", "venture capital", "valuation", "evaluations",
    "corporate finance", "corporate development", "restructuring", "deal advisory",
    "strategy and transactions", "fp&a", "financial planning", "controle de gestion",
    "financial analyst", "analyste financier", "structuring", "leveraged finance",
    "lbo", "ecm", "dcm", "project finance", "working capital", "cash management",
    "business planning", "financial modeling", "modelisation financiere", "equity research",
]

# Intitules strictement rejetes (elimination automatique)
EXCLUDED_KEYWORDS = [
    "audit legal", "audit statutaire", "cac", "commissariat aux comptes",
    "comptabilite generale", "assistant comptable", "comptable unique",
    "comptable fournisseurs", "conseiller clientele", "charge d'accueil", "back office",
    "middle office reglementaire", "kyc", "aml", "conformite",
    "business analyst tech", "actuariat", "data analyst", "developpeur",
    "developer", "software", "saisie comptable", "avocat", "juriste", "legal", "lawyer",
]

# Gestion de la periode de demarrage (multiplicateur de note)
START_MONTH_PENALTIES = {
    "janvier": 1.0, "january": 1.0,
    "fevrier": 0.95, "february": 0.95,
    "mars": 0.80, "march": 0.80,
    "avril": 0.40, "april": 0.40,
    "mai": 0.20, "may": 0.20,
}

# Seuil de score minimal pour envoi sur Telegram (%)
MIN_SCORE_THRESHOLD = 50

# Nombre maximal d'alertes par run (evite le flood / les limites Telegram)
MAX_ALERTS_PER_RUN = 25
