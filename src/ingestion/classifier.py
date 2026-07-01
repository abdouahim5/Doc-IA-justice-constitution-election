"""Classification constitution / élections / justice."""

import re
import unicodedata

_CONSTITUTION_KW = {
    "constitution", "article", "republique", "république", "senat", "sénat",
    "assemblee", "assemblée", "parlement", "conseil constitutionnel",
    "preambule", "préambule", "institution", "loi organique", "mandat",
    "premier ministre", "bloc de constitutionnalite",
    "president", "président", "eligibilite", "éligibilité", "eligib",
}

_ELECTIONS_KW = {
    "election", "élection", "elections", "élections", "vote", "voter", "scrutin",
    "ballotage", "candidat", "presidentielle", "présidentielle", "legislative",
    "législative", "municipale", "europeenne", "européenne", "insee", "abstention",
    "suffrage", "bureau de vote", "participation", "urne", "tour 1", "tour 2",
    "date", "dates", "calendrier", "quand", "dernier", "derniere", "prochain",
}

_JUSTICE_KW = {
    "justice", "jurisprudence", "tribunal", "jugement", "arret", "arrêt",
    "cassation", "cour de cassation", "conseil d'etat", "conseil d'état",
    "legifrance", "légifrance", "code civil", "code penal", "code pénal",
    "procedure", "procédure", "penal", "pénal", "civil", "administratif",
    "avocat", "procureur", "greffe", "litige", "qpc", "decision", "décision",
    "judilibre", "appel", "tgi", "tj", "loi", "decret", "décret", "ordonnance",
    "aide juridictionnelle", "ministere de la justice", "ministère de la justice",
    "delit", "délit", "crime", "infraction", "contravention", "sanction",
    "peine", "prison", "amende", "prescription", "plainte", "prevenu", "prévenu",
    "accuse", "accusé", "correctionnel", "assises", "casier judiciaire",
    "reclusion", "réclusion", "vol", "escroquerie", "violence", "viol", "meurtre",
    "assassinat", "agression", "sexuelle",
}

_TEST_CIVIQUE_KW = {
    "examen civique", "test civique", "formation civique", "livret du citoyen",
    "livret_du_citoyen", "liste officielle des questions", "carte de sejour",
    "carte de séjour", "naturalisation", "contrat d'integration",
    "contrat d'intégration", "formation-civique", "fiches par thematique",
    "fiches par thématique", "charte des droits", "integration republicaine",
    "intégration républicaine", "mise en situation", "questions de connaissance",
    "arrete du 10 octobre 2025", "arrêté du 10 octobre 2025", "test_civique",
    "carte de resident", "carte de résident", "laicite", "laïcité", "citoyen",
}

# Mots isolés → thème (recherche même avec une seule requête)
_SINGLE_WORD_TOPICS: dict[str, str] = {
    "constitution": "constitution",
    "republique": "constitution",
    "parlement": "constitution",
    "senat": "constitution",
    "depute": "constitution",
    "president": "constitution",
    "marianne": "constitution",
    "devise": "constitution",
    "elections": "elections",
    "election": "elections",
    "vote": "elections",
    "voter": "elections",
    "scrutin": "elections",
    "insee": "elections",
    "abstention": "elections",
    "participation": "elections",
    "justice": "justice",
    "tribunal": "justice",
    "qpc": "justice",
    "loi": "justice",
    "lois": "justice",
    "delit": "justice",
    "crime": "justice",
    "crimes": "justice",
    "infraction": "justice",
    "contravention": "justice",
    "penal": "justice",
    "pénal": "justice",
    "sanction": "justice",
    "peine": "justice",
    "plainte": "justice",
    "jurisprudence": "justice",
    "viol": "justice",
    "meurtre": "justice",
    "assassinat": "justice",
    "laicite": "test_civique",
    "naturalisation": "test_civique",
    "citoyen": "test_civique",
    "civique": "test_civique",
    "integration": "test_civique",
    "immigration": "test_civique",
    "france": "general",
    "histoire": "test_civique",
    "geographie": "test_civique",
}


def _fold(text: str) -> str:
    n = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in n if unicodedata.category(c) != "Mn")


def classify_text(text: str, filename: str = "", filepath: str = "") -> str:
    """Retourne constitution | elections | justice | test_civique | general."""
    path_blob = _fold(f"{filepath} {filename}")
    if "/justice/" in path_blob or path_blob.startswith("justice/"):
        return "justice"
    if "sources_officielles/justice" in path_blob.replace("\\", "/"):
        return "justice"
    if any(x in path_blob for x in ("pages_crawlees/j_", "/j_particuliers_vosdroits_f", "crime_viol", "infractions_penales", "code_penal")):
        return "justice"

    blob = _fold(f"{filename} {text[:8000]}")
    if "categorie : test_civique" in blob or "category: test_civique" in blob:
        return "test_civique"
    if any(x in _fold(filename) for x in ("test_civique", "livret_du_citoyen", "liste_questions", "formation_civique", "fc_")):
        return "test_civique"
    if any(x in _fold(filename) for x in ("justice/", "justice_", "j_", "code_penal", "infractions_penales", "delit", "crime")):
        return "justice"
    scores = {
        "constitution": sum(1 for k in _CONSTITUTION_KW if k in blob),
        "elections": sum(1 for k in _ELECTIONS_KW if k in blob),
        "justice": sum(1 for k in _JUSTICE_KW if k in blob),
        "test_civique": sum(1 for k in _TEST_CIVIQUE_KW if k in blob),
    }
    best = max(scores, key=scores.get)
    if scores[best] >= 2:
        return best
    if scores[best] >= 1 and scores[best] > sum(v for k, v in scores.items() if k != best):
        return best
    return "general"


def expand_short_query(question: str) -> str:
    """Enrichit les requêtes très courtes pour améliorer la recherche documentaire."""
    q = question.strip().rstrip("?.!,;:")
    if not q or len(q.split()) > 2:
        return question
    if len(q) < 2:
        return question
    folded = _fold(q)
    _PENAL_SINGLE = {
        "crime": "crime infraction pénale cour d'assises réclusion peine",
        "crimes": "crime infraction pénale cour d'assises",
        "delit": "délit infraction pénale tribunal correctionnel emprisonnement",
        "délit": "délit infraction pénale tribunal correctionnel",
        "delits": "délit infraction pénale sanctions",
        "infraction": "infraction pénale contravention délit crime classification",
        "contravention": "contravention infraction pénale amende tribunal police",
        "loi": "loi droit pénal texte juridique sanctions",
        "lois": "loi droit pénal code législation française",
        "peine": "peine sanction pénale prison amende sursis",
        "sanction": "sanction pénale peine amende prison",
        "plainte": "plainte infraction dépôt police gendarmerie",
        "penal": "droit pénal infraction délit crime sanctions",
        "pénal": "droit pénal infraction délit crime sanctions",
        "viol": "viol crime infraction sexuelle cour d'assises réclusion peine",
        "meurtre": "meurtre crime cour d'assises réclusion homicide",
    }
    if folded in _PENAL_SINGLE:
        return f"{q} — {_PENAL_SINGLE[folded]} (sources officielles)"
    return f"{q} — définition, contexte et rôle en France (sources officielles)"


def enrich_search_query(question: str, topic: str) -> str:
    """Enrichit la requête de recherche selon le thème détecté."""
    base = expand_short_query(question)
    folded = _fold(question)
    if topic == "constitution" and any(
        k in folded for k in ("president", "presidentielle", "eligib", "condition", "candidat")
    ):
        return (
            f"{question} Président de la République élection suffrage universel "
            "éligibilité mandat nationalité parrainages candidat"
        )
    if topic == "elections" and "president" in folded:
        return (
            f"{question} élection présidentielle candidat éligibilité suffrage "
            "scrutin majorité absolue"
        )
    return base


def classify_question(question: str) -> str:
    """Route une question vers le bon agent."""
    raw = question.strip().rstrip("?.!,;:")
    q = _fold(raw)
    if not q:
        return "general"

    tokens = [t for t in q.split() if t]
    if len(tokens) == 1:
        word = tokens[0]
        if word in _SINGLE_WORD_TOPICS:
            return _SINGLE_WORD_TOPICS[word]
        for topic, keywords in (
            ("test_civique", _TEST_CIVIQUE_KW),
            ("constitution", _CONSTITUTION_KW),
            ("elections", _ELECTIONS_KW),
            ("justice", _JUSTICE_KW),
        ):
            if word in {_fold(k) for k in keywords}:
                return topic

    tc_hits = sum(1 for k in _TEST_CIVIQUE_KW if k in q)
    if tc_hits >= 2 or ("examen" in q and "civique" in q):
        return "test_civique"
    if re.search(r"article\s*\d+", q) and not any(k in q for k in ("code", "civil", "penal", "pénal")):
        return "constitution"
    if any(k in q for k in ("president", "presidentielle")) and any(
        k in q for k in ("condition", "eligib", "etre", "être", "candidat", "devenir", "pour")
    ):
        return "constitution"
    if any(k in q for k in ("president", "presidentielle", "pouvoir du president")):
        return "constitution"
    if any(k in q for k in ("pourcent", "chiffre", "taux", "nombre", "combien", "statistique", "resultat")):
        if not any(k in q for k in _JUSTICE_KW):
            return "data"
    j_hits = sum(1 for k in _JUSTICE_KW if k in q)
    e_hits = sum(1 for k in _ELECTIONS_KW if k in q)
    c_hits = sum(1 for k in _CONSTITUTION_KW if k in q)
    if j_hits >= 1 and j_hits >= e_hits and j_hits >= c_hits:
        return "justice"
    if e_hits > c_hits and e_hits >= 1:
        return "elections"
    if c_hits >= 1:
        return "constitution"
    if e_hits >= 1:
        return "elections"
    return "general"
