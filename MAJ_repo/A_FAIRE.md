# Mises a jour du repo job-hunter — a faire en une seule fois

Tout se fait sur github.com, dans le navigateur. Aucun code a ecrire.

## 1) Importer / remplacer les fichiers
Repo -> bouton **Add file** -> **Upload files**.
Ouvre le dossier **MAJ_repo**, selectionne **TOUT son contenu** (les fichiers ET les
dossiers collectors, matcher, utils, config, tools, .github) et glisse-le dans la zone.
Puis en bas -> **Commit changes**.

GitHub remplace automatiquement les anciennes versions de main.py, requirements.txt,
config/settings.py, .github/workflows/automation.yml. Le reste est ajoute.

Fichiers concernes :
- companies.csv
- main.py
- requirements.txt
- collectors/base.py, greenhouse.py, lever.py, smartrecruiters.py
- matcher/evaluator.py
- utils/deduplicator.py
- config/settings.py
- tools/resolve_ats.py
- .github/workflows/automation.yml (remplace) + resolve.yml (nouveau)

## 2) Supprimer les anciens fichiers agregateurs
Ouvre le dossier **scrapers/** dans le repo et supprime ces 4 fichiers
(ouvre chacun -> icone corbeille -> Commit) :
- scrapers/wttj.py
- scrapers/linkedin_xray.py
- scrapers/jobteaser.py
- scrapers/base.py
(config/resume.py n'est plus utilise : tu peux le laisser, sans effet.)

## 3) Verifier les secrets
Repo -> Settings -> Secrets and variables -> Actions. Il faut :
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
(GROQ_API_KEY n'est plus utilise : tu peux le supprimer.)

## 4) Lancer dans le bon ordre (onglet Actions)
a) **Resolveur ATS** -> Run workflow. Il remplit companies.csv avec l'ATS de chaque
   entreprise. La 1re fois c'est long (il teste ~1367 entreprises). Attends la fin.
b) **Job Hunter Automation** -> Run workflow. Verifie que Telegram recoit les offres.

IMPORTANT : tant que le Resolveur (etape 4a) n'a pas tourne au moins une fois,
companies.csv n'a pas d'ATS renseigne -> 0 offre. C'est normal. Apres, tout est
automatique (offres toutes les 3h, resolveur chaque lundi).

## Note
Ignore les dossiers **__pycache__** (fichiers .pyc) : ce sont des fichiers
techniques inutiles, ne les selectionne pas lors de l upload.
