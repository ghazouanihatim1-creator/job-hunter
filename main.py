import os
import requests
from scrapers import get_jobs
from matcher import analyze_job

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Erreur : Variables Telegram manquantes.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        print("✅ Message Telegram envoyé !")
    else:
        print(f"❌ Erreur Telegram : {res.text}")

def main():
    print("🚀 Lancement du Job Hunter...")
    
    # Message direct de test pour valider la réception Telegram
    send_telegram_message("🤖 *Job Hunter Bot* : Connexion réussie ! Recherche d'offres en cours...")

    jobs = get_jobs()
    print(f"📊 {len(jobs)} offres trouvées.")

    for job in jobs:
        analysis = analyze_job(job, GROQ_API_KEY)
        score = analysis.get("match_score", 0)
        
        msg = (
            f"🎯 *Nouvelle Offre ({score}% Match)*\n\n"
            f"🏢 *Entreprise* : {job.get('company')}\n"
            f"📌 *Poste* : {job.get('title')}\n"
            f"📍 *Lieu* : {job.get('location')}\n\n"
            f"💡 *Analyse IA* : {analysis.get('reason')}\n\n"
            f"🔗 [Consulter l'offre]({job.get('url')})"
        )
        send_telegram_message(msg)

if __name__ == "__main__":
    main()
