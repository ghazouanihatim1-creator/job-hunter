"""
Envoi et formatage des alertes Telegram (compatible avec le scoring par regles).
"""
import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_alert(job: dict, analysis: dict) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Token ou Chat ID Telegram manquant.")
        return False

    score = analysis.get("match_score", 0)
    if score >= 80:
        badge = "🔥 *EXCELLENTE OPPORTUNITE*"
    elif score >= 65:
        badge = "🎯 *OPPORTUNITE PERTINENTE*"
    else:
        badge = "📌 *OPPORTUNITE EVALUEE*"

    def clean(x):
        return str(x).replace("*", "").replace("_", "").replace("`", "")

    company = clean(job.get("company", "Non precise"))
    title = clean(job.get("title", "Poste"))
    location = clean(job.get("location", "Non precise"))
    source = clean(job.get("source", "Web"))
    date_pub = clean(job.get("date", "Recemment"))
    summary = clean(analysis.get("summary", ""))
    pros = clean(analysis.get("pros", ""))
    cons = clean(analysis.get("cons", ""))

    message = (
        f"{badge} *({score}%)*\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏢 *Entreprise* : {company}\n"
        f"📌 *Poste* : {title}\n"
        f"📍 *Lieu* : {location}\n"
        f"📅 *Publie* : {date_pub}\n"
        f"🌐 *Source* : {source}\n\n"
        f"📝 {summary}\n\n"
        f"✅ {pros}\n\n"
        f"⚠️ {cons}\n\n"
        f"🔗 [CANDIDATER DIRECTEMENT]({job.get('url')})"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            print(f"Alerte envoyee : {title} ({company})")
            return True
        print(f"Erreur Telegram {res.status_code} : {res.text}")
        return False
    except Exception as e:
        print(f"Erreur envoi Telegram : {e}")
        return False
