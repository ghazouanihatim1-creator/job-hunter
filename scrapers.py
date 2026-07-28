import requests
from bs4 import BeautifulSoup

def get_jobs():
    """Récupère des offres d'emploi récentes en Finance."""
    jobs = []
    
    # Offres de démonstration et tests de scraping
    sample_jobs = [
        {
            "title": "Stage M&A / Transaction Services (H/F)",
            "company": "KPMG France",
            "location": "Paris",
            "url": "https://careers.kpmg.fr",
            "description": "Analyse financière, due diligence, modélisation pour opérations M&A."
        },
        {
            "title": "Analyste FP&A / Contrôle de Gestion Junior",
            "company": "TotalEnergies",
            "location": "La Défense",
            "url": "https://totalenergies.com/careers",
            "description": "Budgeting, reporting financier mensuel, analyse des écarts."
        }
    ]
    
    return sample_jobs
