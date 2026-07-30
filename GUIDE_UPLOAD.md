# Job Hunter — Guide d'upload (rebuild étape 0)

Repo : `github.com/ghazouanihatim1-creator/job-hunter`

## 1. Fichiers à uploader (respecter les dossiers)

| Fichier | Emplacement dans le repo |
|---|---|
| `main.py` | racine |
| `companies.csv` | racine (**1140 entreprises**) |
| `enrich_companies.py` | racine |
| `requirements.txt` | racine |
| `seen_jobs.json` | racine (vidé à `[]` pour repartir propre) |
| `config/settings.py` | `config/` |
| `config/resume.py` | `config/` |
| `scrapers/base.py` | `scrapers/` (bug stage/PFE corrigé) |
| `scrapers/company_boards.py` | `scrapers/` (**nouveau** — boards ATS) |
| `scrapers/wttj.py` | `scrapers/` |
| `scrapers/linkedin_xray.py` | `scrapers/` |
| `scrapers/jobteaser.py` | `scrapers/` |
| `matcher/evaluator.py` | `matcher/` (boost par tier) |
| `utils/companies.py` | `utils/` (**nouveau** — watchlist + découverte) |
| `utils/telegram.py` | `utils/` (digest groupé) |
| `utils/deduplicator.py` | `utils/` |
| `.github/workflows/automation.yml` | `.github/workflows/` |
| `.github/workflows/enrich.yml` | `.github/workflows/` (**nouveau**) |

## 2. À SUPPRIMER dans le repo
- Le dossier parasite **`github/workflows/`** (sans le point) — jamais lu par Actions.

## 3. Secrets GitHub (déjà en place, à vérifier)
`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `GROQ_API_KEY`

## 4. Ordre de lancement
1. Upload de tous les fichiers + suppression du dossier parasite.
2. **Actions → Enrichissement Watchlist → Run workflow** : remplit les colonnes `ats`/`slug` de companies.csv (détection des boards). Optionnel mais recommandé pour activer le filet ATS.
3. **Actions → Job Hunter Automation → Run workflow** : premier run. Le bot scrape, score par IA, envoie le digest Telegram, et ajoute automatiquement les nouvelles boîtes finance découvertes.
4. Ensuite tout tourne seul toutes les 3 h.

## 5. Ce qui a changé vs l'ancienne version
- **Filtre stage/PFE corrigé** : accepte « Stagiaire », « PFE », « fin d'études » (avant : rejetés).
- **Watchlist de 1140 entreprises** classées par tier (Élite/Cible/Autre) → boost de score selon le prestige.
- **Auto-découverte** : la liste grossit chaque jour toute seule (nouvelles boîtes finance ajoutées et committées).
- **Filet ATS** (Greenhouse/Lever/Ashby/SmartRecruiters) pour les boîtes qui en ont.
- **Digest Telegram groupé** (une alerte par run, triée par score) au lieu d'un message par offre.
- **Alerte technique** si un run plante.
- WTTJ ne ramène plus les CDI (stages uniquement) ; LinkedIn extrait le nom d'entreprise.
