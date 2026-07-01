"""Traductions FR / EN pour l'interface Streamlit."""

from __future__ import annotations

import streamlit as st

SUPPORTED_LANGS = ("fr", "en")

APP_NAME = "France Civique IA"

STRINGS: dict[str, dict[str, str]] = {
  # Marque
  "app_name": {"fr": APP_NAME, "en": "France Civics AI"},
  "brand_subtitle": {
      "fr": "Constitution, élections, justice & sources officielles",
      "en": "Constitution, elections, justice & official sources",
  },
  "lang_label": {"fr": "Langue", "en": "Language"},
  "new_conversation": {"fr": "Nouvelle conversation", "en": "New conversation"},
  "sidebar_show": {"fr": "Menu", "en": "Menu"},
  "sidebar_hide": {"fr": "Masquer le menu", "en": "Hide menu"},
  "nav_accueil": {"fr": "Accueil", "en": "Home"},
  "nav_chat": {"fr": "Poser une question", "en": "Ask a question"},
  "nav_france": {"fr": "France Civique", "en": "France Civics"},
  "nav_themes": {"fr": "Thèmes", "en": "Topics"},
  "nav_test_civique": {"fr": "Test de préparation civique", "en": "Civic test prep"},
  "nav_faq": {"fr": "FAQ", "en": "FAQ"},
  "nav_admin": {"fr": "Configuration", "en": "Settings"},
  # Accueil
  "home_badge": {"fr": "🇫🇷 FRANCE CIVIQUE IA", "en": "🇫🇷 FRANCE CIVICS AI"},
  "home_title": {
      "fr": "La Constitution, les élections et la justice, réponses sourcées.",
      "en": "The Constitution, elections and justice, with sourced answers.",
  },
  "home_text": {
      "fr": "Posez vos questions sur le droit constitutionnel, les scrutins électoraux, "
            "la justice et les données officielles — chaque réponse cite ses sources (PostgreSQL, sites gouvernementaux).",
      "en": "Ask about constitutional law, elections, justice and official data — "
            "every answer cites its sources (PostgreSQL, government sites).",
  },
  "home_btn_chat": {"fr": "💬  Poser une question", "en": "💬  Ask a question"},
  "home_btn_themes": {"fr": "📋  Parcourir les thèmes", "en": "📋  Browse topics"},
  "home_stats_title": {"fr": "Votre base documentaire en chiffres", "en": "Your document base in numbers"},
  "home_no_index": {
      "fr": "Aucun document indexé. Allez dans **Configuration** pour indexer vos fichiers.",
      "en": "No indexed documents. Go to **Settings** to index your files.",
  },
  # Chat
  "chat_badge": {"fr": "💬 ASSISTANT IA", "en": "💬 AI ASSISTANT"},
  "chat_title": {"fr": "Posez votre question", "en": "Ask your question"},
  "chat_text": {
      "fr": "Constitution, élections et justice → base PostgreSQL (sources officielles). "
            "Autres sujets → vos documents indexés.",
      "en": "Constitution, elections and justice → PostgreSQL (official sources). "
            "Other topics → your indexed documents.",
  },
  "chat_placeholder": {
      "fr": "Ex : article 2, droits du président...",
      "en": "E.g. article 2, powers of the president...",
  },
  "chat_analyzing": {"fr": "Analyse des documents...", "en": "Analyzing documents..."},
  "chat_llm_error": {
      "fr": "Configuration LLM invalide. Allez dans **Configuration**.",
      "en": "Invalid LLM configuration. Go to **Settings**.",
  },
  # France
  "france_badge": {"fr": "🇫🇷 FRANCE CIVIQUE", "en": "🇫🇷 FRANCE CIVICS"},
  "france_title": {"fr": "Constitution, Élections & Justice", "en": "Constitution, Elections & Justice"},
  "france_text": {
      "fr": "Multi-agent spécialisé : droit constitutionnel, scrutins électoraux, justice "
            "et données chiffrées — indexé dans PostgreSQL (Docker) pour des réponses rapides et sourcées.",
      "en": "Specialized multi-agent: constitutional law, elections, justice and data "
            "— indexed in PostgreSQL (Docker) for fast, sourced answers.",
  },
  "pg_ok": {
      "fr": "🟢 PostgreSQL connecté — base docia_fr (Docker, port 5433)",
      "en": "🟢 PostgreSQL connected — docia_fr database (Docker, port 5433)",
  },
  "pg_ko": {"fr": "🔴 PostgreSQL indisponible — {msg}", "en": "🔴 PostgreSQL unavailable — {msg}"},
  "facts": {"fr": "Faits structurés", "en": "Structured facts"},
  "tables": {"fr": "Tableaux extraits", "en": "Extracted tables"},
  "cache_hits": {"fr": "Réponses en cache", "en": "Cached answers"},
  "pgadmin_title": {"fr": "🐘 Connexion pgAdmin / DBeaver", "en": "🐘 pgAdmin / DBeaver connection"},
  "france_section": {"fr": "Assistant multi-agent", "en": "Multi-agent assistant"},
  "france_placeholder": {
      "fr": "Ex : article 5, QPC, code civil, taux d'abstention...",
      "en": "E.g. article 5, QPC, civil code, abstention rate...",
  },
  "suggestions": {"fr": "💡 Suggestions", "en": "💡 Suggestions"},
  "cache_caption": {"fr": "⚡ Réponse instantanée (cache)", "en": "⚡ Instant answer (cache)"},
  "agent_caption": {"fr": "Agent : **{agent}** · Thème : {topic}", "en": "Agent: **{agent}** · Topic: {topic}"},
  "agent_msg": {"fr": "Agent : **{agent}**", "en": "Agent: **{agent}**"},
  "routing": {"fr": "Routage multi-agent...", "en": "Multi-agent routing..."},
  # Common
  "sources": {"fr": "📎 Sources", "en": "📎 Sources"},
  "ask_btn": {"fr": "Demander", "en": "Ask"},
  "explore_btn": {"fr": "Explorer →", "en": "Explore →"},
  "themes_section": {"fr": "EXPLORER PAR THÈME", "en": "EXPLORE BY TOPIC"},
  "themes_hero_title": {"fr": "Choisissez un domaine", "en": "Choose a topic"},
  "themes_hero_text": {
      "fr": "Chaque thème ouvre une conversation guidée avec les sources officielles indexées.",
      "en": "Each topic starts a guided conversation with indexed official sources.",
  },
  "theme_active": {
      "fr": "Conversation — thème : **{theme}** (vous pouvez enchaîner vos questions)",
      "en": "Conversation — topic: **{theme}** (you can ask follow-up questions)",
  },
  "theme_change_hint": {
      "fr": "Choisissez un autre thème dans le menu pour changer de sujet.",
      "en": "Pick another topic from the menu to change subject.",
  },
  "theme_explore_title": {
      "fr": "Exploration — {theme}",
      "en": "Exploring — {theme}",
  },
  "theme_all_btn": {"fr": "← Tous les thèmes", "en": "← All topics"},
  "theme_resume_btn": {"fr": "Reprendre l'exploration", "en": "Resume exploration"},
  "theme_continue_section": {
      "fr": "Poursuivre l'exploration",
      "en": "Continue exploring",
  },
  "theme_chat_placeholder": {
      "fr": "Posez une question de suite sur {theme}…",
      "en": "Ask a follow-up about {theme}…",
  },
  "tech_detail": {"fr": "Détail technique", "en": "Technical details"},
  "error": {"fr": "Erreur : {msg}", "en": "Error: {msg}"},
  "pg_unavailable": {
      "fr": "PostgreSQL indisponible : {msg}",
      "en": "PostgreSQL unavailable: {msg}",
  },
  "pg_hint": {
      "fr": "Lancez `docker compose up -d` puis `python main.py pg-init` et `pg-ingest`.",
      "en": "Run `docker compose up -d` then `python main.py pg-init` and `pg-ingest`.",
  },
  # Test civique
  "civic_badge": {"fr": "🎓 PRÉPARATION TEST CIVIQUE", "en": "🎓 CIVIC TEST PREPARATION"},
  "civic_title": {
      "fr": "Réussissez le test civique français",
      "en": "Pass the French civic test",
  },
  "civic_text": {
      "fr": "Cours structurés, quiz par thème, examens blancs, révisions ciblées et suivi de votre progression — "
            "alignés sur les 5 thèmes officiels du test civique.",
      "en": "Structured courses, themed quizzes, mock exams, targeted revision and progress tracking — "
            "aligned with the 5 official civic test themes.",
  },
  "civic_tab_overview": {"fr": "Vue d'ensemble", "en": "Overview"},
  "civic_tab_courses": {"fr": "Cours", "en": "Courses"},
  "civic_tab_quiz": {"fr": "Quiz", "en": "Quiz"},
  "civic_tab_exam": {"fr": "Examen blanc", "en": "Mock exam"},
  "civic_tab_review": {"fr": "Révisions", "en": "Revision"},
  "civic_tab_progress": {"fr": "Progression", "en": "Progress"},
  "civic_stat_courses": {"fr": "Cours lus", "en": "Courses read"},
  "civic_stat_quiz": {"fr": "Quiz", "en": "Quiz"},
  "civic_stat_exam": {"fr": "Examens", "en": "Exams"},
  "civic_stat_review": {"fr": "À réviser", "en": "To review"},
  "civic_modules_title": {"fr": "Les 5 thèmes officiels", "en": "The 5 official themes"},
  "civic_open_course": {"fr": "Ouvrir le cours →", "en": "Open course →"},
  "civic_btn_quiz": {"fr": "📝 Lancer un quiz", "en": "📝 Start a quiz"},
  "civic_btn_exam": {"fr": "📋 Examen blanc", "en": "📋 Mock exam"},
  "civic_btn_review": {"fr": "🔄 Réviser mes erreurs", "en": "🔄 Review mistakes"},
  "civic_select_module": {"fr": "Choisir un module", "en": "Choose a module"},
  "civic_mark_read": {"fr": "Marquer comme lu", "en": "Mark as read"},
  "civic_course_done": {"fr": "Cours enregistré dans votre progression.", "en": "Course saved to your progress."},
  "civic_already_read": {"fr": "✓ Module déjà consulté", "en": "✓ Module already read"},
  "civic_quiz_this_module": {"fr": "Passer le quiz de ce module", "en": "Take this module's quiz"},
  "civic_quiz_module": {"fr": "Module du quiz", "en": "Quiz module"},
  "civic_quiz_hint": {"fr": "{n} questions — répondez puis validez.", "en": "{n} questions — answer then submit."},
  "civic_no_questions": {"fr": "Aucune question pour ce module.", "en": "No questions for this module."},
  "civic_submit_quiz": {"fr": "Valider le quiz", "en": "Submit quiz"},
  "civic_choose": {"fr": "Choisir une réponse", "en": "Choose an answer"},
  "civic_correct": {"fr": "Bonne réponse", "en": "Correct"},
  "civic_wrong": {"fr": "Mauvaise réponse", "en": "Wrong"},
  "civic_score": {"fr": "Score", "en": "Score"},
  "civic_retry_quiz": {"fr": "Recommencer le quiz", "en": "Retry quiz"},
  "civic_exam_intro_title": {"fr": "Simulation d'examen", "en": "Exam simulation"},
  "civic_exam_intro": {
      "fr": "Un examen blanc mélange des questions de tous les thèmes, comme le test civique officiel.",
      "en": "A mock exam mixes questions from all themes, like the official civic test.",
  },
  "civic_exam_format": {
      "fr": "**{n} questions** — seuil de réussite conseillé : **{pass_pct} %**.",
      "en": "**{n} questions** — recommended pass threshold: **{pass_pct}%**.",
  },
  "civic_start_exam": {"fr": "Commencer l'examen blanc", "en": "Start mock exam"},
  "civic_exam_progress": {"fr": "Question {cur}/{total}", "en": "Question {cur}/{total}"},
  "civic_question_n": {"fr": "Question {n}", "en": "Question {n}"},
  "civic_finish_exam": {"fr": "Terminer et corriger", "en": "Finish and grade"},
  "civic_exam_pass": {
      "fr": "🎉 Félicitations ! {score}/{total} ({pct} %) — objectif atteint.",
      "en": "🎉 Congratulations! {score}/{total} ({pct}%) — goal reached.",
  },
  "civic_exam_fail": {
      "fr": "📚 {score}/{total} ({pct} %) — consultez les cours et révisez vos erreurs.",
      "en": "📚 {score}/{total} ({pct}%) — review courses and your mistakes.",
  },
  "civic_new_exam": {"fr": "Nouvel examen blanc", "en": "New mock exam"},
  "civic_go_review": {"fr": "Réviser mes erreurs →", "en": "Review mistakes →"},
  "civic_no_review": {"fr": "Aucune erreur à réviser — continuez comme ça !", "en": "Nothing to review — keep it up!"},
  "civic_review_intro": {
      "fr": "**{n} question(s)** à retravailler selon vos réponses incorrectes.",
      "en": "**{n} question(s)** to rework based on your wrong answers.",
  },
  "civic_clear_review": {"fr": "Tout marquer comme maîtrisé", "en": "Mark all as mastered"},
  "civic_progress_detail": {"fr": "Avancement global", "en": "Overall progress"},
  "civic_prog_courses": {"fr": "Cours complétés", "en": "Courses completed"},
  "civic_prog_quiz": {"fr": "Réussite aux quiz", "en": "Quiz success rate"},
  "civic_prog_exam": {"fr": "Meilleur examen blanc", "en": "Best mock exam"},
  "civic_by_module": {"fr": "Détail par module", "en": "Per module"},
  "civic_col_course": {"fr": "Cours", "en": "Course"},
  "civic_col_quiz": {"fr": "Quiz", "en": "Quiz"},
  "civic_exam_history": {"fr": "Historique des examens", "en": "Exam history"},
  "civic_attempt_n": {"fr": "Tentative {n}", "en": "Attempt {n}"},
  "civic_reset": {"fr": "Réinitialiser la progression", "en": "Reset progress"},
  "civic_reset_done": {"fr": "Progression réinitialisée.", "en": "Progress reset."},
}

NAV_KEYS = [
    ("accueil", "🏠", "nav_accueil"),
    ("chat", "💬", "nav_chat"),
    ("france", "🇫🇷", "nav_france"),
    ("themes", "📋", "nav_themes"),
    ("test_civique", "🎓", "nav_test_civique"),
    ("faq", "❓", "nav_faq"),
    ("admin", "⚙️", "nav_admin"),
]

FRANCE_SUGGESTIONS_I18N = [
    {
        "title": {"fr": "Calendrier", "en": "Calendar"},
        "question": {
            "fr": "Quelles sont les dates des derniers scrutins en France ?",
            "en": "What are the dates of the most recent elections in France?",
        },
        "desc": {
            "fr": "Présidentielle, législatives, européennes",
            "en": "Presidential, legislative, European elections",
        },
    },
    {
        "title": {"fr": "Constitution", "en": "Constitution"},
        "question": {
            "fr": "Que dit l'article 2 de la Constitution ?",
            "en": "What does Article 2 of the Constitution say?",
        },
        "desc": {"fr": "Symboles de la République", "en": "Symbols of the Republic"},
    },
    {
        "title": {"fr": "Élections", "en": "Elections"},
        "question": {
            "fr": "Comment se déroule une élection présidentielle ?",
            "en": "How does a presidential election work?",
        },
        "desc": {"fr": "Scrutin et tours de vote", "en": "Ballot and voting rounds"},
    },
    {
        "title": {"fr": "Justice", "en": "Justice"},
        "question": {
            "fr": "Qu'est-ce que la question prioritaire de constitutionnalité (QPC) ?",
            "en": "What is the priority constitutional question (QPC)?",
        },
        "desc": {
            "fr": "QPC, cours, jurisprudence",
            "en": "QPC, courts, case law",
        },
    },
    {
        "title": {"fr": "Chiffres", "en": "Data"},
        "question": {
            "fr": "Quel est le taux de participation aux élections ?",
            "en": "What is the voter turnout rate in elections?",
        },
        "desc": {"fr": "Données chiffrées indexées", "en": "Indexed numerical data"},
    },
]

THEME_CARDS_I18N = [
    {
        "id": "constitution",
        "icon": "📜",
        "color": "#2563eb",
        "title": {"fr": "Constitution", "en": "Constitution"},
        "desc": {
            "fr": "Articles, symboles de la République, révisions",
            "en": "Articles, symbols of the Republic, amendments",
        },
        "source": {
            "fr": "Conseil constitutionnel · Légifrance",
            "en": "Constitutional Council · Légifrance",
        },
        "question": {
            "fr": "Que dit l'article 2 de la Constitution ?",
            "en": "What does Article 2 of the Constitution say?",
        },
    },
    {
        "id": "elections",
        "icon": "🗳️",
        "color": "#ea580c",
        "title": {"fr": "Élections", "en": "Elections"},
        "desc": {
            "fr": "Présidentielle, législatives, européennes, municipales",
            "en": "Presidential, legislative, European, local elections",
        },
        "source": {
            "fr": "data.gouv.fr · Ministère de l'Intérieur",
            "en": "data.gouv.fr · Ministry of the Interior",
        },
        "question": {
            "fr": "Comment se déroule une élection présidentielle ?",
            "en": "How does a presidential election work?",
        },
    },
    {
        "id": "justice",
        "icon": "⚖️",
        "color": "#1e3a5f",
        "title": {"fr": "Justice & Droit", "en": "Justice & Law"},
        "desc": {
            "fr": "Lois, codes, procédure, jurisprudence et tribunaux",
            "en": "Laws, codes, procedure, case law and courts",
        },
        "source": {
            "fr": "Légifrance · Cour de cassation · Conseil d'État",
            "en": "Légifrance · Court of Cassation · Council of State",
        },
        "question": {
            "fr": "Qu'est-ce que la question prioritaire de constitutionnalité (QPC) ?",
            "en": "What is the priority constitutional question (QPC)?",
        },
    },
    {
        "id": "institutions",
        "icon": "🏛️",
        "color": "#00A651",
        "title": {"fr": "Institutions", "en": "Institutions"},
        "desc": {
            "fr": "Président, Parlement, gouvernement, Conseil",
            "en": "President, Parliament, government, Council",
        },
        "source": {
            "fr": "service-public.fr · vie-publique.fr",
            "en": "service-public.fr · vie-publique.fr",
        },
        "question": {
            "fr": "Quels sont les pouvoirs du Président de la République ?",
            "en": "What are the powers of the President of the Republic?",
        },
    },
    {
        "id": "calendrier",
        "icon": "📅",
        "color": "#0284c7",
        "title": {"fr": "Calendrier", "en": "Calendar"},
        "desc": {
            "fr": "Dates des scrutins, tours de vote, prochaines échéances",
            "en": "Election dates, voting rounds, upcoming polls",
        },
        "source": {
            "fr": "Calendrier officiel · vie-publique.fr",
            "en": "Official calendar · vie-publique.fr",
        },
        "question": {
            "fr": "Quelles sont les dates des derniers scrutins en France ?",
            "en": "What are the dates of the most recent elections in France?",
        },
    },
    {
        "id": "chiffres",
        "icon": "📊",
        "color": "#dc2626",
        "title": {"fr": "Chiffres & résultats", "en": "Data & results"},
        "desc": {
            "fr": "Participation, abstention, résultats par région",
            "en": "Turnout, abstention, results by region",
        },
        "source": {
            "fr": "INSEE · data.gouv.fr 2022–2024",
            "en": "INSEE · data.gouv.fr 2022–2024",
        },
        "question": {
            "fr": "Quel est le taux de participation aux dernières élections ?",
            "en": "What was the turnout in the latest elections?",
        },
    },
    {
        "id": "citoyennete",
        "icon": "🎓",
        "color": "#7c3aed",
        "title": {"fr": "Citoyenneté", "en": "Citizenship"},
        "desc": {
            "fr": "Droit de vote, inscription, bureau de vote",
            "en": "Voting rights, registration, polling station",
        },
        "source": {
            "fr": "service-public.fr · électeurs",
            "en": "service-public.fr · voters",
        },
        "question": {
            "fr": "Comment s'inscrire sur les listes électorales ?",
            "en": "How do you register on the electoral rolls?",
        },
    },
]

THEME_FOLLOWUPS_I18N: dict[str, list[dict]] = {
    "constitution": [
        {
            "question": {"fr": "et l'article 3 ?", "en": "and article 3?"},
            "desc": {"fr": "Souveraineté nationale", "en": "National sovereignty"},
        },
        {
            "question": {"fr": "article 5", "en": "article 5"},
            "desc": {"fr": "Rôle du Président", "en": "Role of the President"},
        },
        {
            "question": {"fr": "Qu'est-ce que la laïcité ?", "en": "What is secularism (laïcité)?"},
            "desc": {"fr": "Article 1er", "en": "Article 1"},
        },
    ],
    "elections": [
        {
            "question": {"fr": "Quelles sont les dates des dernières élections ?", "en": "What are the latest election dates?"},
            "desc": {"fr": "Calendrier électoral", "en": "Election calendar"},
        },
        {
            "question": {"fr": "Comment fonctionne le second tour ?", "en": "How does the second round work?"},
            "desc": {"fr": "Majorité absolue", "en": "Absolute majority"},
        },
    ],
    "justice": [
        {
            "question": {"fr": "Qu'est-ce qu'un délit ?", "en": "What is a misdemeanor (délit)?"},
            "desc": {"fr": "Droit pénal", "en": "Criminal law"},
        },
        {
            "question": {"fr": "Quelle différence entre crime et délit ?", "en": "Difference between crime and délit?"},
            "desc": {"fr": "Classification pénale", "en": "Penal classification"},
        },
    ],
    "institutions": [
        {
            "question": {"fr": "condition pour etre president", "en": "requirements to be president"},
            "desc": {"fr": "Éligibilité", "en": "Eligibility"},
        },
        {
            "question": {"fr": "Quels sont les pouvoirs du Premier ministre ?", "en": "Powers of the Prime Minister?"},
            "desc": {"fr": "Gouvernement", "en": "Government"},
        },
    ],
    "calendrier": [
        {
            "question": {"fr": "Quand a eu lieu la dernière présidentielle ?", "en": "When was the last presidential election?"},
            "desc": {"fr": "Avril 2022", "en": "April 2022"},
        },
        {
            "question": {"fr": "Prochaines élections en France", "en": "Upcoming elections in France"},
            "desc": {"fr": "Échéances", "en": "Deadlines"},
        },
    ],
    "chiffres": [
        {
            "question": {"fr": "taux d'abstention présidentielle 2022", "en": "abstention rate 2022 presidential"},
            "desc": {"fr": "Participation", "en": "Turnout"},
        },
        {
            "question": {"fr": "résultats élection présidentielle 2022", "en": "2022 presidential election results"},
            "desc": {"fr": "Résultats", "en": "Results"},
        },
    ],
    "citoyennete": [
        {
            "question": {"fr": "Qui peut voter en France ?", "en": "Who can vote in France?"},
            "desc": {"fr": "Électeurs", "en": "Voters"},
        },
        {
            "question": {"fr": "Comment trouver son bureau de vote ?", "en": "How to find your polling station?"},
            "desc": {"fr": "Vote", "en": "Voting"},
        },
    ],
}

# Legacy liste courte
THEME_SUGGESTIONS_I18N = [
    {
        "title": {"fr": "Constitution", "en": "Constitution"},
        "question": {"fr": "article 2", "en": "article 2"},
        "desc": {
            "fr": "Langue, drapeau, hymne et devise de la République",
            "en": "Language, flag, anthem and motto of the Republic",
        },
    },
    {
        "title": {"fr": "Institutions", "en": "Institutions"},
        "question": {
            "fr": "Quels sont les droits du president",
            "en": "What are the powers of the president",
        },
        "desc": {
            "fr": "Pouvoirs du Président de la République",
            "en": "Powers of the President of the Republic",
        },
    },
    {
        "title": {"fr": "Recherche", "en": "Search"},
        "question": {"fr": "Marseillaise", "en": "Marseillaise"},
        "desc": {
            "fr": "Trouver le mot dans tous les documents",
            "en": "Find the word across all documents",
        },
    },
    {
        "title": {"fr": "Technique", "en": "Technical"},
        "question": {"fr": "Qu'est-ce que le RAG ?", "en": "What is RAG?"},
        "desc": {
            "fr": "Comprendre le fonctionnement de l'agent",
            "en": "Understand how the agent works",
        },
    },
]


def get_lang() -> str:
    lang = st.session_state.get("lang", "fr")
    return lang if lang in SUPPORTED_LANGS else "fr"


def t(key: str, **kwargs) -> str:
    lang = get_lang()
    text = STRINGS.get(key, {}).get(lang, STRINGS.get(key, {}).get("fr", key))
    return text.format(**kwargs) if kwargs else text


def localized_prompt(question: str) -> str:
    """Ajoute une consigne de langue pour les réponses LLM."""
    if get_lang() == "en":
        return f"{question}\n\n[Please answer in English.]"
    return question


def get_nav_items() -> list[tuple[str, str, str]]:
    return [(key, icon, t(label_key)) for key, icon, label_key in NAV_KEYS]


def get_france_suggestions() -> list[tuple[str, str, str]]:
    lang = get_lang()
    return [
        (s["title"][lang], s["question"][lang], s["desc"][lang])
        for s in FRANCE_SUGGESTIONS_I18N
    ]


def get_theme_cards() -> list[dict]:
    lang = get_lang()
    return [
        {
            "id": c["id"],
            "icon": c["icon"],
            "color": c["color"],
            "title": c["title"][lang],
            "desc": c["desc"][lang],
            "source": c["source"][lang],
            "question": c["question"][lang],
        }
        for c in THEME_CARDS_I18N
    ]


def get_theme_followups(theme_id: str) -> list[dict]:
    lang = get_lang()
    items = THEME_FOLLOWUPS_I18N.get(theme_id, [])
    return [
        {
            "question": item["question"][lang],
            "desc": item["desc"][lang],
        }
        for item in items
    ]


def get_theme_suggestions() -> list[tuple[str, str, str]]:
    lang = get_lang()
    return [
        (s["title"][lang], s["question"][lang], s["desc"][lang])
        for s in THEME_SUGGESTIONS_I18N
    ]
