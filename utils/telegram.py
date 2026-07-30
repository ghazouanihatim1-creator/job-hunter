"""
Envoi et formatage des alertes Telegram.
- send_digest : UN digest groupé par run (toutes les offres retenues), trié par
  score puis fraîcheur, découpé automatiquement si > limite Telegram.
- send_error_alert : alerte technique si un run plante.
"""

import os
import requests
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TG_LIMIT = 3800  # marge sous la limite Telegram de 4096 caractères


def _clean(text) -> str:
    return str(text).replace("*", "").replace("_", "").replace("`", "").replace("[", "(").replace("]", ")")


def _send_message(text: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram Token ou Chat ID manquant.")
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    try:
        res = requests.post(url, json=payload, timeout=15)
        if res.status_code == 200:
            return True
        print(f"❌ Erreur Telegram ({res.status_code}) : {res.text}")
        return False
    except Exception as e:
        print(f"❌ Erreur envoi Telegram : {e}")
        return False


def _badge(score: int) -> str:
    if score >= 80:
        return "🔥"
    if score >= 70:
        return "🎯"
    return "📌"


def _format_offer(job: dict, analysis: dict, idx: int) -> str:
    score = analysis.get("match_score", 0)
    company = _clean(job.get("company", "Non précisée"))
    title = _clean(job.get("title", "Poste Finance"))
    location = _clean(job.get("location", "Non précisé"))
    source = _clean(job.get("source", "Web"))
    tier = analysis.get("tier", "")
    tier_str = f" · {tier}" if tier else ""
    pitch = _clean(analysis.get("pitch", "")).strip()
    url = job.get("url", "")

    block = (
        f"{_badge(score)} *{idx}. {title}* — {score}%\n"
        f"🏢 {company}{tier_str}\n"
        f"📍 {location}  ·  🌐 {source}\n"
    )
    if pitch:
        block += f"💬 _{pitch[:220]}_\n"
    if url:
        block += f"🔗 [Candidater]({url})\n"
    return block + "\n"


def send_digest(results: list) -> int:
    """
    results : liste de tuples (job, analysis) déjà filtrés au-dessus du seuil.
    Envoie un digest groupé (multi-messages si nécessaire). Retourne le nb d'offres.
    """
    if not results:
        print("ℹ️ Aucune offre à envoyer dans le digest.")
        return 0

    # Tri : score décroissant
    results = sorted(results, key=lambda r: r[1].get("match_score", 0), reverse=True)

    header = (
        f"🗞️ *DIGEST JOB HUNTER — {datetime.now().strftime('%d/%m/%Y %H:%M')}*\n"
        f"*{len(results)} opportunité(s) stage/PFE finance détectée(s)*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    messages, current = [], header
    for idx, (job, analysis) in enumerate(results, start=1):
        block = _format_offer(job, analysis, idx)
        if len(current) + len(block) > TG_LIMIT:
            messages.append(current)
            current = ""
        current += block
    if current.strip():
        messages.append(current)

    sent = 0
    for i, msg in enumerate(messages):
        if len(messages) > 1:
            msg = f"_(partie {i+1}/{len(messages)})_\n" + msg
        if _send_message(msg):
            sent += 1
    print(f"✅ Digest envoyé ({len(results)} offres, {sent}/{len(messages)} message(s)).")
    return len(results)


def send_error_alert(context: str, error: str) -> bool:
    """Alerte technique en cas de plantage d'un run."""
    msg = (
        f"⚠️ *JOB HUNTER — ALERTE TECHNIQUE*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        f"📍 Étape : {_clean(context)}\n"
        f"❌ Erreur : {_clean(error)[:500]}"
    )
    return _send_message(msg)
