"""Contenu pédagogique aligné sur les thèmes du test civique français."""

from __future__ import annotations

from typing import Any

# Thèmes officiels (naturalisation / titre de séjour)
MODULES: list[dict[str, Any]] = [
    {
        "id": "principes",
        "icon": "🗽",
        "color": "#2563eb",
        "title": {
            "fr": "Principes et valeurs de la République",
            "en": "Principles and values of the Republic",
        },
        "summary": {
            "fr": "Liberté, égalité, fraternité, laïcité, symboles nationaux.",
            "en": "Liberty, equality, fraternity, secularism, national symbols.",
        },
        "lessons": [
            {
                "title": {"fr": "Devise et symboles", "en": "Motto and symbols"},
                "body": {
                    "fr": (
                        "La devise **Liberté, Égalité, Fraternité** figure dans la Constitution. "
                        "Les symboles de la République sont le **drapeau tricolore** (bleu, blanc, rouge), "
                        "l'**hymne national** (La Marseillaise) et **Marianne**. "
                        "Le 14 juillet commémore la prise de la Bastille (1789) et la Fête de la Fédération (1790)."
                    ),
                    "en": (
                        "The motto **Liberty, Equality, Fraternity** is in the Constitution. "
                        "Republic symbols: the **tricolor flag**, **La Marseillaise**, and **Marianne**. "
                        "July 14 marks the Bastille storming (1789) and the Festival of the Federation (1790)."
                    ),
                },
            },
            {
                "title": {"fr": "Laïcité", "en": "Secularism"},
                "body": {
                    "fr": (
                        "La **laïcité** garantit la liberté de conscience et la neutralité de l'État. "
                        "Elle est inscrite dans la loi de 1905. L'État ne favorise aucune religion ; "
                        "chacun est libre de croire ou de ne pas croire. Dans les services publics, "
                        "les agents et les usagers doivent respecter la neutralité religieuse."
                    ),
                    "en": (
                        "**Secularism** guarantees freedom of conscience and state neutrality. "
                        "Enshrined in the 1905 law, the State favors no religion; everyone may believe or not. "
                        "In public services, staff and users must respect religious neutrality."
                    ),
                },
            },
        ],
    },
    {
        "id": "institutions",
        "icon": "🏛️",
        "color": "#00A651",
        "title": {
            "fr": "Système institutionnel et politique",
            "en": "Institutional and political system",
        },
        "summary": {
            "fr": "Président, Parlement, gouvernement, décentralisation, Union européenne.",
            "en": "President, Parliament, government, decentralization, European Union.",
        },
        "lessons": [
            {
                "title": {"fr": "Le Président et le Parlement", "en": "President and Parliament"},
                "body": {
                    "fr": (
                        "Le **Président de la République** est élu au suffrage universel direct pour 5 ans. "
                        "Il nomme le Premier ministre et peut dissoudre l'Assemblée nationale. "
                        "Le **Parlement** comprend l'**Assemblée nationale** (577 députés) et le **Sénat** (348 sénateurs). "
                        "Il vote les lois et contrôle le gouvernement."
                    ),
                    "en": (
                        "The **President** is elected by direct universal suffrage for 5 years. "
                        "They appoint the Prime Minister and may dissolve the National Assembly. "
                        "**Parliament** includes the **National Assembly** (577 MPs) and the **Senate** (348 senators). "
                        "It passes laws and oversees the government."
                    ),
                },
            },
            {
                "title": {"fr": "Collectivités et UE", "en": "Local government and EU"},
                "body": {
                    "fr": (
                        "La France est organisée en **régions**, **départements**, **communes** et d'autres collectivités. "
                        "Les maires gèrent les communes ; les conseils régionaux et départementaux ont leurs compétences propres. "
                        "La France est membre de l'**Union européenne** depuis 1957 (traités de Rome) ; "
                        "la monnaie est l'**euro** depuis 2002."
                    ),
                    "en": (
                        "France is organized into **regions**, **departments**, **municipalities** and other bodies. "
                        "Mayors run municipalities; regional and departmental councils have their own powers. "
                        "France has been in the **European Union** since 1957; the **euro** has been used since 2002."
                    ),
                },
            },
        ],
    },
    {
        "id": "droits",
        "icon": "⚖️",
        "color": "#1e3a5f",
        "title": {
            "fr": "Droits et devoirs",
            "en": "Rights and duties",
        },
        "summary": {
            "fr": "Droits fondamentaux, obligations civiques, justice.",
            "en": "Fundamental rights, civic duties, justice.",
        },
        "lessons": [
            {
                "title": {"fr": "Droits fondamentaux", "en": "Fundamental rights"},
                "body": {
                    "fr": (
                        "La **Déclaration des droits de l'homme et du citoyen** (1789) proclame la liberté, "
                        "la propriété, la sûreté et la résistance à l'oppression. "
                        "Toute personne a droit à la **liberté d'expression**, à un **procès équitable** "
                        "et à la protection contre les discriminations. L'**égalité femmes-hommes** est un principe constitutionnel."
                    ),
                    "en": (
                        "The **Declaration of the Rights of Man and of the Citizen** (1789) proclaims liberty, "
                        "property, security and resistance to oppression. Everyone has **freedom of expression**, "
                        "a **fair trial** and protection from discrimination. **Gender equality** is constitutional."
                    ),
                },
            },
            {
                "title": {"fr": "Devoirs du citoyen", "en": "Citizen duties"},
                "body": {
                    "fr": (
                        "Les devoirs incluent le **respect des lois**, le **paiement des impôts**, "
                        "la **défense de la patrie** (via la JDC pour les jeunes) et le respect de l'**ordre public**. "
                        "Le vote n'est pas obligatoire en France, mais l'inscription sur les listes électorales l'est pour les citoyens français."
                    ),
                    "en": (
                        "Duties include **respecting laws**, **paying taxes**, "
                        "**national defense** (via civic service for youth) and **public order**. "
                        "Voting is not mandatory, but French citizens must register on electoral rolls."
                    ),
                },
            },
        ],
    },
    {
        "id": "histoire",
        "icon": "📚",
        "color": "#ea580c",
        "title": {
            "fr": "Histoire, géographie et culture",
            "en": "History, geography and culture",
        },
        "summary": {
            "fr": "Repères historiques, territoire, patrimoine culturel.",
            "en": "Historical landmarks, territory, cultural heritage.",
        },
        "lessons": [
            {
                "title": {"fr": "Repères historiques", "en": "Historical landmarks"},
                "body": {
                    "fr": (
                        "La **Révolution française** (1789) abolit l'Ancien Régime et proclame les droits. "
                        "La **IIIe République** (1875) établit l'école gratuite, laïque et obligatoire. "
                        "En **1945**, la France est libérée ; la IVe puis la **Ve République** (1958) instaurent l'ordre actuel."
                    ),
                    "en": (
                        "The **French Revolution** (1789) ended the Ancien Régime and proclaimed rights. "
                        "The **Third Republic** (1875) established free, secular, compulsory schooling. "
                        "In **1945** France was liberated; the Fourth then **Fifth Republic** (1958) shaped today's system."
                    ),
                },
            },
            {
                "title": {"fr": "Territoire et capitale", "en": "Territory and capital"},
                "body": {
                    "fr": (
                        "La **capitale** est **Paris**. La France métropolitaine compte 13 régions (depuis 2016). "
                        "Elle possède aussi des **départements et territoires d'outre-mer** (DROM-COM). "
                        "Les fleuves majeurs : Seine, Loire, Garonne, Rhône. La France partage des frontières avec plusieurs pays européens."
                    ),
                    "en": (
                        "The **capital** is **Paris**. Metropolitan France has 13 regions (since 2016). "
                        "It also has **overseas departments and territories** (DROM-COM). "
                        "Major rivers: Seine, Loire, Garonne, Rhône. France borders several European countries."
                    ),
                },
            },
        ],
    },
    {
        "id": "vivre",
        "icon": "🤝",
        "color": "#0284c7",
        "title": {
            "fr": "Vivre dans la société française",
            "en": "Living in French society",
        },
        "summary": {
            "fr": "Travail, santé, école, engagement citoyen.",
            "en": "Work, health, school, civic engagement.",
        },
        "lessons": [
            {
                "title": {"fr": "Travail et protection sociale", "en": "Work and social protection"},
                "body": {
                    "fr": (
                        "Le **code du travail** fixe la durée légale du travail (35 h/semaine), le SMIC et les congés payés. "
                        "La **Sécurité sociale** couvre maladie, famille, retraite. "
                        "Pour travailler, il faut souvent un **contrat de travail** ; le chômage est indemnisé sous conditions par France Travail (ex-Pôle emploi)."
                    ),
                    "en": (
                        "The **labor code** sets legal working time (35 h/week), minimum wage and paid leave. "
                        "**Social security** covers health, family and pensions. "
                        "Work usually requires an **employment contract**; unemployment benefits are available under conditions via France Travail."
                    ),
                },
            },
            {
                "title": {"fr": "École et citoyenneté", "en": "School and citizenship"},
                "body": {
                    "fr": (
                        "L'**école est obligatoire** de 3 à 16 ans. Elle est gratuite et laïque dans le public. "
                        "Les associations jouent un rôle important dans la vie locale. "
                        "Respecter autrui, lutter contre les **discriminations** et participer à la vie collective font partie de l'intégration."
                    ),
                    "en": (
                        "**School is compulsory** from ages 3 to 16. Public school is free and secular. "
                        "Associations play a key role locally. "
                        "Respecting others, fighting **discrimination** and joining community life are part of integration."
                    ),
                },
            },
        ],
    },
]

QUESTIONS: list[dict[str, Any]] = [
    {
        "id": "q_principes_1",
        "module_id": "principes",
        "question": {
            "fr": "Quelle est la devise de la République française ?",
            "en": "What is the motto of the French Republic?",
        },
        "choices": {
            "fr": ["Liberté, Égalité, Fraternité", "Honneur et Patrie", "Travail, Famille, Patrie", "Unité, Justice, Progrès"],
            "en": ["Liberty, Equality, Fraternity", "Honor and Fatherland", "Work, Family, Fatherland", "Unity, Justice, Progress"],
        },
        "correct": 0,
        "explanation": {
            "fr": "Article 2 de la Constitution de 1958.",
            "en": "Article 2 of the 1958 Constitution.",
        },
    },
    {
        "id": "q_principes_2",
        "module_id": "principes",
        "question": {
            "fr": "Quelle loi fondatrice organise la laïcité en France ?",
            "en": "Which founding law organizes secularism in France?",
        },
        "choices": {
            "fr": ["Loi de 1905", "Loi de 1881", "Loi de 1958", "Loi de 2000"],
            "en": ["1905 law", "1881 law", "1958 law", "2000 law"],
        },
        "correct": 0,
        "explanation": {
            "fr": "Loi du 9 décembre 1905 sur la séparation des Églises et de l'État.",
            "en": "Law of 9 December 1905 on separation of Churches and State.",
        },
    },
    {
        "id": "q_principes_3",
        "module_id": "principes",
        "question": {
            "fr": "Quelle fête nationale française est célébrée le 14 juillet ?",
            "en": "Which national holiday is celebrated on July 14 in France?",
        },
        "choices": {
            "fr": ["Fête nationale", "Armistice", "Noël", "Toussaint"],
            "en": ["National Day", "Armistice Day", "Christmas", "All Saints' Day"],
        },
        "correct": 0,
        "explanation": {
            "fr": "Commémore la prise de la Bastille et la Fête de la Fédération.",
            "en": "Commemorates the Bastille and the Festival of the Federation.",
        },
    },
    {
        "id": "q_institutions_1",
        "module_id": "institutions",
        "question": {
            "fr": "Pour combien de temps le Président de la République est-il élu ?",
            "en": "For how long is the President of the Republic elected?",
        },
        "choices": {
            "fr": ["5 ans", "6 ans", "7 ans", "4 ans"],
            "en": ["5 years", "6 years", "7 years", "4 years"],
        },
        "correct": 0,
        "explanation": {
            "fr": "Mandat de 5 ans (quinquennat) depuis 2002.",
            "en": "5-year term (quinquennat) since 2002.",
        },
    },
    {
        "id": "q_institutions_2",
        "module_id": "institutions",
        "question": {
            "fr": "Le Parlement français est composé de :",
            "en": "The French Parliament consists of:",
        },
        "choices": {
            "fr": [
                "L'Assemblée nationale et le Sénat",
                "Le Conseil constitutionnel et le Sénat",
                "L'Assemblée nationale et le Conseil d'État",
                "Le Sénat et le gouvernement",
            ],
            "en": [
                "National Assembly and Senate",
                "Constitutional Council and Senate",
                "National Assembly and Council of State",
                "Senate and government",
            ],
        },
        "correct": 0,
        "explanation": {
            "fr": "Article 24 de la Constitution.",
            "en": "Article 24 of the Constitution.",
        },
    },
    {
        "id": "q_institutions_3",
        "module_id": "institutions",
        "question": {
            "fr": "Quelle monnaie est utilisée en France ?",
            "en": "Which currency is used in France?",
        },
        "choices": {
            "fr": ["L'euro", "Le franc", "Le dollar", "La livre"],
            "en": ["Euro", "Franc", "Dollar", "Pound"],
        },
        "correct": 0,
        "explanation": {
            "fr": "L'euro est en circulation depuis le 1er janvier 2002.",
            "en": "The euro has been in circulation since 1 January 2002.",
        },
    },
    {
        "id": "q_droits_1",
        "module_id": "droits",
        "question": {
            "fr": "En quelle année a été adoptée la Déclaration des droits de l'homme et du citoyen ?",
            "en": "When was the Declaration of the Rights of Man and of the Citizen adopted?",
        },
        "choices": {
            "fr": ["1789", "1792", "1804", "1958"],
            "en": ["1789", "1792", "1804", "1958"],
        },
        "correct": 0,
        "explanation": {
            "fr": "Adoptée pendant la Révolution française.",
            "en": "Adopted during the French Revolution.",
        },
    },
    {
        "id": "q_droits_2",
        "module_id": "droits",
        "question": {
            "fr": "Le vote est-il obligatoire pour les élections en France ?",
            "en": "Is voting mandatory in French elections?",
        },
        "choices": {
            "fr": ["Non, mais l'inscription sur les listes l'est pour les citoyens", "Oui, toujours", "Non, jamais d'inscription", "Oui, seulement aux municipales"],
            "en": ["No, but registration is required for citizens", "Yes, always", "No, never register", "Yes, only local elections"],
        },
        "correct": 0,
        "explanation": {
            "fr": "Le vote est un droit, pas une obligation ; l'inscription électorale est obligatoire.",
            "en": "Voting is a right, not a duty; electoral registration is mandatory.",
        },
    },
    {
        "id": "q_droits_3",
        "module_id": "droits",
        "question": {
            "fr": "L'égalité entre les femmes et les hommes est :",
            "en": "Gender equality is:",
        },
        "choices": {
            "fr": ["Un principe constitutionnel", "Une simple recommandation", "Interdite par la loi", "Réservée au travail"],
            "en": ["A constitutional principle", "A mere recommendation", "Forbidden by law", "Only for work"],
        },
        "correct": 0,
        "explanation": {
            "fr": "Inscrit dans la Constitution (article 1er).",
            "en": "Enshrined in the Constitution (Article 1).",
        },
    },
    {
        "id": "q_histoire_1",
        "module_id": "histoire",
        "question": {
            "fr": "Quelle révolution a commencé en 1789 ?",
            "en": "Which revolution began in 1789?",
        },
        "choices": {
            "fr": ["La Révolution française", "La Révolution industrielle", "La Commune de Paris", "La Révolution de Juillet"],
            "en": ["French Revolution", "Industrial Revolution", "Paris Commune", "July Revolution"],
        },
        "correct": 0,
        "explanation": {
            "fr": "Elle marque la fin de l'Ancien Régime.",
            "en": "It marks the end of the Ancien Régime.",
        },
    },
    {
        "id": "q_histoire_2",
        "module_id": "histoire",
        "question": {
            "fr": "Quelle est la capitale de la France ?",
            "en": "What is the capital of France?",
        },
        "choices": {
            "fr": ["Paris", "Lyon", "Marseille", "Bordeaux"],
            "en": ["Paris", "Lyon", "Marseille", "Bordeaux"],
        },
        "correct": 0,
        "explanation": {
            "fr": "Paris est aussi le siège des institutions nationales.",
            "en": "Paris is also the seat of national institutions.",
        },
    },
    {
        "id": "q_histoire_3",
        "module_id": "histoire",
        "question": {
            "fr": "La Ve République date de :",
            "en": "The Fifth Republic dates from:",
        },
        "choices": {
            "fr": ["1958", "1945", "1875", "1792"],
            "en": ["1958", "1945", "1875", "1792"],
        },
        "correct": 0,
        "explanation": {
            "fr": "Nouvelle Constitution adoptée sous de Gaulle.",
            "en": "New Constitution adopted under de Gaulle.",
        },
    },
    {
        "id": "q_vivre_1",
        "module_id": "vivre",
        "question": {
            "fr": "L'école est obligatoire en France de :",
            "en": "School is compulsory in France from:",
        },
        "choices": {
            "fr": ["3 à 16 ans", "6 à 18 ans", "5 à 15 ans", "4 à 17 ans"],
            "en": ["3 to 16", "6 to 18", "5 to 15", "4 to 17"],
        },
        "correct": 0,
        "explanation": {
            "fr": "Instruction obligatoire de 3 à 16 ans (loi de 2019).",
            "en": "Compulsory education from 3 to 16 (2019 law).",
        },
    },
    {
        "id": "q_vivre_2",
        "module_id": "vivre",
        "question": {
            "fr": "Quelle durée légale du travail s'applique en France (temps plein) ?",
            "en": "What is the legal full-time working week in France?",
        },
        "choices": {
            "fr": ["35 heures", "40 heures", "38 heures", "42 heures"],
            "en": ["35 hours", "40 hours", "38 hours", "42 hours"],
        },
        "correct": 0,
        "explanation": {
            "fr": "Durée légale hebdomadaire dans le code du travail.",
            "en": "Legal weekly duration in the labor code.",
        },
    },
    {
        "id": "q_vivre_3",
        "module_id": "vivre",
        "question": {
            "fr": "L'école publique en France est :",
            "en": "Public school in France is:",
        },
        "choices": {
            "fr": ["Gratuite et laïque", "Payante et religieuse", "Gratuite mais privée", "Obligatoire seulement jusqu'à 12 ans"],
            "en": ["Free and secular", "Paid and religious", "Free but private", "Compulsory only until 12"],
        },
        "correct": 0,
        "explanation": {
            "fr": "Principes de la IIIe République, toujours en vigueur.",
            "en": "Third Republic principles still in force.",
        },
    },
]


def get_modules() -> list[dict[str, Any]]:
    return MODULES


def get_module(module_id: str) -> dict[str, Any] | None:
    return next((m for m in MODULES if m["id"] == module_id), None)


def get_questions_for_module(module_id: str) -> list[dict[str, Any]]:
    return [q for q in QUESTIONS if q["module_id"] == module_id]


def get_question(question_id: str) -> dict[str, Any] | None:
    return next((q for q in QUESTIONS if q["id"] == question_id), None)


def get_exam_questions(count: int = 12) -> list[dict[str, Any]]:
    """Une question par module en priorité, puis complément."""
    by_module: dict[str, list[dict[str, Any]]] = {}
    for q in QUESTIONS:
        by_module.setdefault(q["module_id"], []).append(q)
    picked: list[dict[str, Any]] = []
    for mod in MODULES:
        qs = by_module.get(mod["id"], [])
        if qs:
            picked.append(qs[0])
    remaining = [q for q in QUESTIONS if q not in picked]
    for q in remaining:
        if len(picked) >= count:
            break
        picked.append(q)
    return picked[:count]


def questions_count_by_module() -> dict[str, int]:
    counts: dict[str, int] = {}
    for q in QUESTIONS:
        counts[q["module_id"]] = counts.get(q["module_id"], 0) + 1
    return counts


def localized(obj: dict, key: str, lang: str) -> str:
    val = obj.get(key, {})
    if isinstance(val, dict):
        return val.get(lang, val.get("fr", ""))
    return str(val)
