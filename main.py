"""
Orchestrateur - Job Hunter (sources ATS directes, sans agregateurs, sans IA payante).
Sequence : companies.csv -> collecteurs ATS -> filtres/scoring local -> anti-doublon -> Telegram.
"""
import csv
from collectors.greenhouse import GreenhouseCollector
from collectors.lever import LeverCollector
from collectors.smartrecruiters import SmartRecruitersCollector
from matcher.evaluator import evaluate_job
from utils.deduplicator import load_state, save_state, was_notified, record_seen, mark_notified
from utils.telegram import send_telegram_alert
from config.settings import MIN_SCORE_THRESHOLD, MAX_ALERTS_PER_RUN

COLLECTORS = [GreenhouseCollector, LeverCollector, SmartRecruitersCollector]


def load_companies(path="companies.csv"):
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def run_pipeline():
    print("=== DEMARRAGE JOB HUNTER (sources ATS) ===")
    companies = load_companies()
    state = load_state()
    print(f"Entreprises chargees : {len(companies)} | memoire : {len(state)} offres")

    all_offers = []
    for Collector in COLLECTORS:
        subset = [c for c in companies
                  if (c.get("ats_type", "") or "").strip().lower() == Collector.ats_type]
        if not subset:
            continue
        try:
            print(f"-> {Collector.ats_type} : {len(subset)} entreprises...")
            all_offers.extend(Collector(subset).fetch())
        except Exception as e:
            print(f"Collecteur {Collector.ats_type} KO : {e}")

    print(f"Offres brutes recuperees : {len(all_offers)}")

    to_send = []
    for job in all_offers:
        oid = job.get("offer_id")
        if not oid or was_notified(oid, state):
            continue
        record_seen(job, state)
        analysis = evaluate_job(job)
        if analysis.get("rejected"):
            continue
        if analysis.get("match_score", 0) >= MIN_SCORE_THRESHOLD:
            job["_score"] = analysis["match_score"]
            to_send.append((job, analysis))

    # Tri : meilleur matching d'abord (les offres du jour ont un bonus -> remontent)
    to_send.sort(key=lambda x: x[0]["_score"], reverse=True)
    print(f"Offres pertinentes a notifier : {len(to_send)}")

    sent = 0
    for job, analysis in to_send:
        if sent >= MAX_ALERTS_PER_RUN:
            print(f"Plafond {MAX_ALERTS_PER_RUN} atteint, le reste partira au prochain run.")
            break
        if send_telegram_alert(job, analysis):
            mark_notified(job["offer_id"], state)  # marque APRES envoi reussi
            sent += 1

    save_state(state)
    print(f"=== FIN : {sent} alerte(s) envoyee(s) ===")


if __name__ == "__main__":
    run_pipeline()
