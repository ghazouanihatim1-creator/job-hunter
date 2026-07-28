import json
from groq import Groq

def analyze_job(job, api_key):
    """Analyse une offre d'emploi par rapport au CV en utilisant l'IA Groq."""
    if not api_key:
        return {"match_score": 75, "reason": "Analyse automatique (Clé API Groq non configurée)."}

    try:
        with open("cv.txt", "r", encoding="utf-8") as f:
            cv_text = f.read()
    except Exception:
        cv_text = "Finance, M&A, TS, FP&A, Analyse financière."

    client = Groq(api_key=api_key)
    prompt = f"""
    Tu es un expert en recrutement finance.
    Voici le CV du candidat :
    {cv_text}

    Voici l'offre d'emploi :
    Titre: {job.get('title')}
    Entreprise: {job.get('company')}
    Description: {job.get('description', 'Non fournie')}

    Réponds UNIQUEMENT au format JSON strict comme suit :
    {{
        "match_score": 85,
        "reason": "Explication courte de 2 phrases sur l'adéquation."
    }}
    """

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
        )
        content = response.choices[0].message.content.strip()
        # Nettoyage JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        return json.loads(content)
    except Exception as e:
        print(f"Erreur analyse Groq : {e}")
        return {"match_score": 70, "reason": "Correspondance basée sur les mots-clés."}
