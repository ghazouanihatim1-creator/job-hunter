"""
Script d'audit global pour tester chaque composant indépendamment.
"""

import os
import requests
from groq import Groq

def check_env():
    print("=== 1. VÉRIFICATION DES SECRETS / ENVIRONNEMENT ===")
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    groq_key = os.getenv("GROQ_API_KEY")

    print(f"TELEGRAM_BOT_TOKEN: {'✅ PRÉSENT' if token else '❌ MANQUANT'}")
    print(f"TELEGRAM_CHAT_ID: {'✅ PRÉSENT' if chat_id else '❌ MANQUANT'}")
    print(f"GROQ_API_KEY: {'✅ PRÉSENT' if groq_key else '❌ MANQUANT'}")
    return token, chat_id, groq_key

def test_telegram(token, chat_id):
    print("\n=== 2. TEST D'ENVOI TELEGRAM ===")
    if not token or not chat_id:
        print("❌ Impossible de tester Telegram (identifiants manquants).")
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "🧪 *TEST AUDIT JOB HUNTER* : Si tu reçois ce message, Telegram fonctionne à 100% !",
        "parse_mode": "Markdown"
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            print("✅ MESSAGE TELEGRAM ENVOYÉ AVEC SUCCÈS ! Vérifie ton téléphone.")
        else:
            print(f"❌ Échec Telegram ({res.status_code}) : {res.text}")
    except Exception as e:
        print(f"❌ Erreur connexion Telegram : {e}")

def test_groq(groq_key):
    print("\n=== 3. TEST DE L'API GROQ ===")
    if not groq_key:
        print("❌ Impossible de tester Groq (clé manquante).")
        return
    try:
        client = Groq(api_key=groq_key)
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": "Dis 'OK' en JSON strict: {\"status\": \"OK\"}"}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        print(f"✅ Groq répond correctement : {res.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Erreur connexion Groq : {e}")

def test_scrapers():
    print("\n=== 4. TEST DES SCRAPERS ===")
    from scrapers.wttj import WTTJScraper
    from scrapers.linkedin_xray import LinkedInXRayScraper
    from scrapers.jobteaser import JobTeaserScraper

    scrapers = [WTTJScraper(), LinkedInXRayScraper(), JobTeaserScraper()]
    for s in scrapers:
        try:
            jobs = s.fetch_jobs()
            print(f"🟢 Scraper [{s.name}] -> {len(jobs)} offres trouvées.")
            if len(jobs) > 0:
                print(f"   Exemple d'offre : {jobs[0].get('title')} ({jobs[0].get('url')})")
        except Exception as e:
            print(f"🔴 Erreur Scraper [{s.name}] : {e}")

if __name__ == "__main__":
    print("🚀 --- DÉBUT DU DIAGNOSTIC COMPLET ---\n")
    token, chat_id, groq_key = check_env()
    test_telegram(token, chat_id)
    test_groq(groq_key)
    test_scrapers()
    print("\n🏁 --- FIN DU DIAGNOSTIC ---")
