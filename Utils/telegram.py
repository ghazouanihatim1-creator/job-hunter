"""
Module d'envoi et de formatage des alertes Telegram.
"""

import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(job: dict, analysis: dict) -> bool:
    """Formatage strict selon les spécifications et envoi sur Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram Token ou Chat ID manquant dans l'environnement.")
        return False

    score = analysis.get("match_score", 0)
    
    # Indicateur visuel selon la probabilité
    if score >= 80:
        badge = "🔥 *EXCELLENTE OPPORTUNITÉ*"
    elif score >= 70:
        badge = "🎯 *OPPORTUNITÉ PERTINENTE*"
    else:
        badge = "📌 *OPPORTUNITÉ AVALUÉE*"

    # Nettoyage des textes pour éviter les bugs de parse_mode Markdown sur Telegram
    company = job.get("company", "Non précisée").replace("*", "").replace("_", "")
    title = job.get("title", "Poste Finance").replace("*", "").replace("_", "")
    location = job.get("location", "Non précisé").replace("*", "").replace("_", "")
    source = job.get("source", "Web").replace("*", "").replace("_", "")
    date_pub = job.get("date", "Récemment").replace("*", "").replace("_", "")

    message = (
        f"{badge} *({score}% de chance d'entretien)*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏢 *Entreprise* : {company}\n"
        f"📌 *Poste* : {title}\n"
        f"📍 *Lieu* : {location}\n"
        f"📅 *Publié le* : {date_pub}\n"
        f"🌐 *Source* : {source}\n\n"
        f"📝 *Résumé de l'offre* :\n{analysis.get('summary', 'Analyse automatique de l\'offre.')}\n\n"
        f"✅ *Pourquoi ça matche* :\n{analysis.get('pros', 'Excellente adéquation de profil.')}\n\n"
        f"⚠️ *Points faibles / Vigilance* :\n{analysis.get('cons', 'Aucun point bloquant majeur.')}\n\n"
        f"💬 *Pitch rapide (à utiliser)* :\n`{analysis.get('pitch', '')}`\n\n"
        f"🔗 [CANDIDATER DIRECTEMENT]({job.get('url')})"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }

    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            print(f"✅ Alerte envoyée pour : {title} ({company})")
            return True
        else:
            print(f"❌ Erreur Telegram ({res.status_code}) : {res.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur envoi Telegram : {e}")
        return False
