"""
Orchestrateur du Job Hunter.

Séquence :
  1. Charge la watchlist (companies.csv) + la mémoire anti-doublon.
  2. Lance les scrapers (ATS boards + agrégateurs) de façon résiliente.
  3. Déduplique, puis pour chaque offre nouvelle :
       - AUTO-DÉCOUVERTE : ajoute la boîte à la watchlist si finance et inconnue.
       - Scoring IA (Groq) + boost selon le tier de l'entreprise.
  4. Envoie UN digest Telegram groupé (offres >= seuil), trié par score.
  5. Sauvegarde mémoire + watchlist (companies.csv committé par GitHub Actions).
  6. En cas de plantage global : alerte technique Telegram.
"""

import traceback

from config.settings import MIN_SCORE_THRESHOLD, ENABLE_DISCOVERY
from utils.deduplicator import load_seen_jobs, save_seen_jobs, is_already_seen, mark_as_seen
from utils.telegram import send_digest, send_error_alert
from utils.companies import get_registry
from matcher.evaluator import evaluate_job_with_ai, apply_tier_boost

from scrapers.company_boards import CompanyBoardsScraper
from scrapers.wttj import WTTJScraper
from scrapers.linkedin_xray import LinkedInXRayScraper
from scrapers.jobteaser import JobTeaserScraper


def run_pipeline():
    print("🚀 === DÉMARRAGE DU JOB HUNTER ===")

    registry = get_registry()
    seen_jobs = load_seen_jobs()
    print(f"📦 Mémoire : {len(seen_jobs)} offres déjà traitées.")

    scrapers = [
        CompanyBoardsScraper(),   # filet 1 : boards ATS de tes cibles
        WTTJScraper(),            # filet 3 : agrégateurs
        LinkedInXRayScraper(),
        JobTeaserScraper(),
    ]

    all_raw_jobs = []
    for scraper in scrapers:
        try:
            all_raw_jobs.extend(scraper.fetch_jobs())
        except Exception as e:
            print(f"❌ Scraper {scraper.name} en échec : {e}")

    print(f"\n📊 Total brut : {len(all_raw_jobs)} offres.")

    # Déduplication
    new_jobs = []
    for job in all_raw_jobs:
        url = job.get("url")
        if not url or is_already_seen(url, seen_jobs):
            continue
        new_jobs.append(job)
    print(f"✨ Nouvelles offres à évaluer : {len(new_jobs)}\n")

    results = []
    discoveries = 0

    for idx, job in enumerate(new_jobs, start=1):
        company = job.get("company", "")
        title = job.get("title", "")
        print(f"[{idx}/{len(new_jobs)}] {title} — {company} ({job.get('source')})")
        mark_as_seen(job.get("url"), seen_jobs)

        # Tier de l'entreprise (si déjà ciblée)
        tier = registry.tier_of(company)

        # Auto-découverte : nouvelle boîte finance inconnue -> watchlist
        if ENABLE_DISCOVERY and not tier and registry.discover(company):
            discoveries += 1
            tier = "Découverte"

        # Scoring IA + boost tier
        analysis = evaluate_job_with_ai(job)
        analysis = apply_tier_boost(analysis, tier)
        score = analysis.get("match_score", 0)
        print(f"   -> Score : {score}%" + (f" (tier {tier})" if tier else ""))

        if score >= MIN_SCORE_THRESHOLD and not analysis.get("rejected", False):
            results.append((job, analysis))

    # Digest groupé
    sent = send_digest(results)

    # Sauvegardes
    save_seen_jobs(seen_jobs)
    if discoveries:
        registry.save()
        print(f"🌱 {discoveries} nouvelle(s) entreprise(s) ajoutée(s) à la watchlist.")

    print(f"\n✅ === FIN DU RUN : {sent} offre(s) envoyée(s), "
          f"{discoveries} découverte(s) ===")


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as e:
        print(f"💥 Plantage global : {e}")
        traceback.print_exc()
        send_error_alert("run_pipeline", str(e))
        raise
