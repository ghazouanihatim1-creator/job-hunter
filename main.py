"""
Main Orchestrator - Job Hunter Bot
Gère la séquence globale : Scraping -> Anti-Doublon -> Scoring IA -> Alerte Telegram
"""

import sys
from utils.deduplicator import load_seen_jobs, save_seen_jobs, is_already_seen, mark_as_seen
from utils.telegram import send_telegram_alert
from matcher.evaluator import evaluate_job_with_ai
from config.settings import MIN_SCORE_THRESHOLD

# Importation résiliente des scrapers
from scrapers.wttj import WTTJScraper
from scrapers.linkedin_xray import LinkedInXRayScraper
from scrapers.jobteaser import JobTeaserScraper

def run_pipeline():
    print("🚀 === DÉMARRAGE DU JOB HUNTER INDUSTRIAL ===")

    # Étape 1 : Chargement de la mémoire anti-doublon
    seen_jobs = load_seen_jobs()
    print(f"📦 Mémoire chargée : {len(seen_jobs)} offres déjà traitées.")

    # Étape 2 : Initialisation des scrapers (Isolation et Résilience)
    scrapers = [
        WTTJScraper(),
        LinkedInXRayScraper(),
        JobTeaserScraper()
    ]

    all_raw_jobs = []

    # Étape 3 : Exécution sécurisée des scrapers (Si un flanche, les autres continuent)
    for scraper in scrapers:
        try:
            jobs = scraper.fetch_jobs()
            all_raw_jobs.extend(jobs)
        except Exception as e:
            print(f"❌ Erreur critique lors de l'exécution du scraper {scraper.name} : {e}")

    print(f"\n📊 Total brut d'offres récupérées : {len(all_raw_jobs)}")

    # Étape 4 : Déduplication immédiate
    new_jobs = []
    for job in all_raw_jobs:
        job_url = job.get("url")
        if not job_url or is_already_seen(job_url, seen_jobs):
            continue
        new_jobs.append(job)

    print(f"✨ Nouvelles offres uniques à évaluer : {len(new_jobs)}\n")

    alert_count = 0

    # Étape 5 : Traitement et Scoring IA par offre
    for idx, job in enumerate(new_jobs, start=1):
        job_url = job.get("url")
        title = job.get("title")
        company = job.get("company")
        source = job.get("source")

        print(f"[{idx}/{len(new_jobs)}] Évaluation : {title} chez {company} ({source})...")

        # Marquage direct en mémoire pour éviter toute tentative future même en cas d'échec
        mark_as_seen(job_url, seen_jobs)

        # Évaluation par le moteur IA Groq
        analysis = evaluate_job_with_ai(job)
        score = analysis.get("match_score", 0)

        print(f"   -> Score attribué : {score}%")

        # Filtrage par le seuil de score défini
        if score >= MIN_SCORE_THRESHOLD and not analysis.get("rejected", False):
            print("   -> 🎯 Score valide ! Envoi de l'alerte sur Telegram...")
            sent = send_telegram_alert(job, analysis)
            if sent:
                alert_count += 1
        else:
            reason = analysis.get('reason', 'Score sous le seuil minimal')
            print(f"   -> ⏩ Ignorée : {reason}")

    # Étape 6 : Sauvegarde de la mémoire mise à jour
    save_seen_jobs(seen_jobs)

    print(f"\n✅ === FIN DU RUN : {alert_count} alerte(s) envoyée(s) sur Telegram ===")

if __name__ == "__main__":
    run_pipeline()
