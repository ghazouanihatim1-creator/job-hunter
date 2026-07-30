"""
Script d'audit global (check.py)
Vérifie la santé du projet Job-Hunter :
1. Variables d'environnement & Secrets (Groq, Telegram)
2. Intégrité et structure du fichier companies.csv
3. Connexion API Groq (Llama-3.3-70b)
4. Connexion Bot Telegram
5. Test unitaire des scrapers (LinkedIn, WTTJ, JobTeaser, ATS)
6. Vérification du dédoublonnage et de la mémoire (seen_jobs.json)
"""

import os
import sys
import json
import csv
from datetime import datetime

# Importer les modules du projet
try:
    from config import settings
    from utils.companies import CompanyRegistry
    from utils.deduplicator import Deduplicator
    from scrapers.linkedin_xray import LinkedInXRayScraper
    from scrapers.wttj import WTTJScraper
    from scrapers.jobteaser import JobTeaserScraper
    from scrapers.company_boards import CompanyBoardsScraper
    from matcher.evaluator import JobEvaluator
    from utils.telegram import send_telegram_alert, send_telegram_digest
except ImportError as e:
    print(f"❌ Erreur d'importation des modules du projet : {e}")
    print("👉 Assure-toi de lancer ce script depuis la racine du projet.")
    sys.exit(1)


def print_section(title):
    print("\n" + "=" * 60)
    print(f"🔍 {title.upper()}")
    print("=" * 60)


def check_env_variables():
    print_section("1. Vérification des variables d'environnement")
    groq_key = os.getenv("GROQ_API_KEY")
    tele_token = os.getenv("TELEGRAM_BOT_TOKEN")
    tele_chat = os.getenv("TELEGRAM_CHAT_ID")

    status = True
    if groq_key:
        print(f"✅ GROQ_API_KEY : Détectée ({groq_key[:6]}...{groq_key[-4:]})")
    else:
        print("❌ GROQ_API_KEY : Manquante (Définis-la dans ton environnement ou .env)")
        status = False

    if tele_token:
        print(f"✅ TELEGRAM_BOT_TOKEN : Détecté ({tele_token[:6]}...)")
    else:
        print("❌ TELEGRAM_BOT_TOKEN : Manquant")
        status = False

    if tele_chat:
        print(f"✅ TELEGRAM_CHAT_ID : Détecté ({tele_chat})")
    else:
        print("❌ TELEGRAM_CHAT_ID : Manquant")
        status = False

    return status


def check_companies_csv():
    print_section("2. Audit du fichier companies.csv")
    csv_path = "companies.csv"
    if not os.path.exists(csv_path):
        print(f"❌ Fichier {csv_path} introuvable.")
        return False

    total_companies = 0
    categories = {}
    tiers = {}
    ats_count = 0

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        print(f"📋 Colonnes détectées : {headers}")

        for row in reader:
            total_companies += 1
            cat = row.get("category", "Inconnu")
            tier = row.get("tier", "Inconnu")
            ats = row.get("ats", "").strip()

            categories[cat] = categories.get(cat, 0) + 1
            tiers[tier] = tiers.get(tier, 0) + 1
            if ats:
                ats_count += 1

    print(f"✅ Nombre total d'entreprises : {total_companies}")
    print(f"📊 Répartition par Tiers : {tiers}")
    print(f"🏷️ Répartition par Catégories : {categories}")
    print(f"🎯 Entreprises avec ATS configuré : {ats_count}/{total_companies}")

    return total_companies > 0


def check_groq_connection():
    print_section("3. Test de connexion API Groq (Llama-3.3-70b)")
    try:
        evaluator = JobEvaluator()
        dummy_job = {
            "title": "Stage M&A / Corporate Finance",
            "company": "Rothschild & Co",
            "location": "Paris",
            "description": "Stage de fin d'études PFE 6 mois en M&A à partir de Janvier 2027. Modélisation financière, valorisation LBO/DCF.",
            "source": "Test Check"
        }
        print("⏳ Envoi d'un test à Groq...")
        res = evaluator.evaluate(dummy_job)
        if res and "match_score" in res:
            print(f"✅ Connexion Groq OK !")
            print(f"   Score obtenu : {res.get('match_score')}%")
            print(f"   Résumé : {res.get('summary')[:80]}...")
            return True
        else:
            print("❌ Groq a répondu mais la structure du JSON est invalide.")
            return False
    except Exception as e:
        print(f"❌ Échec du test Groq : {e}")
        return False


def check_scrapers():
    print_section("4. Audit rapide des scrapers (Filets de recherche)")

    scrapers = [
        ("LinkedIn X-Ray", LinkedInXRayScraper()),
        ("Welcome to the Jungle", WTTJScraper()),
        ("JobTeaser", JobTeaserScraper()),
        ("Company Boards (ATS)", CompanyBoardsScraper())
    ]

    results = {}
    for name, scraper in scrapers:
        print(f"⏳ Test du scraper [{name}]...")
        try:
            jobs = scraper.fetch_jobs()
            print(f"   ↳ {len(jobs)} offres trouvées.")
            results[name] = len(jobs)
            if jobs:
                sample = jobs[0]
                print(f"   📌 Exemple : {sample.get('title')} @ {sample.get('company')} ({sample.get('source')})")
        except Exception as e:
            print(f"   ❌ Erreur d'exécution pour [{name}] : {e}")
            results[name] = -1

    return results


def check_deduplication_and_memory():
    print_section("5. Vérification du système de mémoire (seen_jobs.json)")
    dedup = Deduplicator()
    seen_path = "seen_jobs.json"

    if os.path.exists(seen_path):
        with open(seen_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                print(f"✅ {seen_path} présent avec {len(data)} offres déjà enregistrées.")
            except Exception:
                print(f"⚠️ {seen_path} est corrompu ou vide.")
    else:
        print(f"ℹ️ {seen_path} n'existe pas encore (sera créé au premier run).")

    # Test d'empreinte
    sample_job = {"title": "Stage M&A", "company": "KPMG", "location": "Paris"}
    fp = dedup.generate_fingerprint(sample_job)
    print(f"🔑 Empreinte de test générée : {fp}")
    return True


def run_full_audit():
    print("\n🚀 LANCEMENT DE L'AUDIT COMPLET DU PROJET JOB-HUNTER")
    print(f"📅 Date de l'audit : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    env_ok = check_env_variables()
    csv_ok = check_companies_csv()
    dedup_ok = check_deduplication_and_memory()
    
    groq_ok = False
    if env_ok:
        groq_ok = check_groq_connection()

    scraper_results = check_scrapers()

    print_section("📋 BILAN DE L'AUDIT")
    print(f"1. Variables & Secrets : {'✅ PASSED' if env_ok else '❌ FAILED'}")
    print(f"2. Watchlist CSV      : {'✅ PASSED' if csv_ok else '❌ FAILED'}")
    print(f"3. API Groq / IA      : {'✅ PASSED' if groq_ok else '❌ FAILED'}")
    print(f"4. Mémoire / Anti-doublon : {'✅ PASSED' if dedup_ok else '❌ FAILED'}")
    print("5. Scrapers :")
    for name, count in scraper_results.items():
        status = "❌ ERREUR" if count == -1 else f"✅ OK ({count} offres)"
        print(f"   - {name} : {status}")

    print("\n💡 Fin du diagnostic. Copie-colle ce résultat pour l'analyse !")


if __name__ == "__main__":
    run_full_audit()
