"""Sources officielles — lois, jurisprudence, délits, crimes et justice pénale."""



from src.scraping.spec import SourceSpec



# URLs testées : service-public.gouv.fr, justice.gouv.fr, justice.fr

# (Légifrance bloque le scraping HTTP 403 — synthèse Code pénal en fichier local)



JUSTICE_CRAWL_SEEDS: list[str] = [

    "https://www.service-public.gouv.fr/particuliers/vosdroits/N19807",
    "https://www.service-public.gouv.fr/particuliers/vosdroits/F1157",
    "https://www.justice.gouv.fr/justice-france/justice-penale",

    "https://www.justice.gouv.fr/justice-france/justice-penale/infractions-penales",

    "https://www.justice.gouv.fr/justice-france/justice-penale/procedure-penale",

]



JUSTICE_SOURCES: list[SourceSpec] = [

    # --- Portails ---

    SourceSpec(

        id="justice_fr_portail",

        title="justice.fr — portail de la justice",

        url="https://www.justice.fr/",

        category="justice",

        kind="html",

        filename="justice/justice_fr_portail.txt",

        publisher="justice.fr",

    ),

    SourceSpec(

        id="ministere_justice",

        title="Ministère de la Justice — portail",

        url="https://www.justice.gouv.fr/",

        category="justice",

        kind="html",

        filename="justice/ministere_justice_portail.txt",

        publisher="Ministère de la Justice",

    ),

    SourceSpec(

        id="sp_justice_hub",

        title="Justice — thème service-public.gouv.fr",

        url="https://www.service-public.gouv.fr/particuliers/vosdroits/N19807",

        category="justice",

        kind="html",

        filename="justice/sp_justice_hub.txt",

        publisher="service-public.gouv.fr",

    ),

    # --- Droit et accès ---

    SourceSpec(

        id="sp_acces_droit_justice",

        title="Accès au droit et à la justice (service-public.gouv.fr)",

        url="https://www.service-public.gouv.fr/particuliers/vosdroits/N261",

        category="justice",

        kind="html",

        filename="justice/justice_acces_droit_service_public.txt",

        publisher="service-public.gouv.fr",

    ),

    SourceSpec(

        id="sp_juridictions",

        title="Juridictions en France (service-public.gouv.fr)",

        url="https://www.service-public.gouv.fr/particuliers/vosdroits/N253",

        category="justice",

        kind="html",

        filename="justice/justice_juridictions_service_public.txt",

        publisher="service-public.gouv.fr",

    ),

    SourceSpec(

        id="sp_aide_juridictionnelle",

        title="Aide juridictionnelle lors d'une procédure en France",

        url="https://www.service-public.gouv.fr/particuliers/vosdroits/F18074",

        category="justice",

        kind="html",

        filename="justice/aide_juridictionnelle.txt",

        publisher="service-public.gouv.fr",

    ),

    SourceSpec(

        id="sp_qpc",

        title="Question prioritaire de constitutionnalité (QPC)",

        url="https://www.service-public.gouv.fr/particuliers/vosdroits/F21088",

        category="justice",

        kind="html",

        filename="justice/qpc_service_public.txt",

        publisher="service-public.gouv.fr",

    ),

    # --- Infractions, délits, crimes ---

    SourceSpec(

        id="sp_infractions_penales",

        title="Infractions pénales : contravention, délit et crime",

        url="https://www.service-public.gouv.fr/particuliers/vosdroits/F1157",

        category="justice",

        kind="html",

        filename="justice/infractions_penales_delit_crime.txt",

        publisher="service-public.gouv.fr",

    ),

    SourceSpec(

        id="mj_infractions_penales",

        title="Les infractions pénales — Ministère de la Justice",

        url="https://www.justice.gouv.fr/justice-france/justice-penale/infractions-penales",

        category="justice",

        kind="html",

        filename="justice/mj_infractions_penales.txt",

        publisher="Ministère de la Justice",

    ),

    SourceSpec(

        id="sp_juridictions_penales",

        title="Juridictions pénales en France",

        url="https://www.service-public.gouv.fr/particuliers/vosdroits/F2189",

        category="justice",

        kind="html",

        filename="justice/juridictions_penales.txt",

        publisher="service-public.gouv.fr",

    ),

    SourceSpec(

        id="sp_prescription_penale",

        title="Justice pénale — délais de prescription",

        url="https://www.service-public.gouv.fr/particuliers/vosdroits/F31982",

        category="justice",

        kind="html",

        filename="justice/prescription_penale.txt",

        publisher="service-public.gouv.fr",

    ),

    SourceSpec(

        id="sp_porter_plainte",

        title="Porter plainte pour une infraction",

        url="https://www.service-public.gouv.fr/particuliers/vosdroits/F35460",

        category="justice",

        kind="html",

        filename="justice/porter_plainte.txt",

        publisher="service-public.gouv.fr",

    ),

    SourceSpec(

        id="sp_avocat_proces_penal",

        title="Avocat obligatoire dans un procès pénal",

        url="https://www.service-public.gouv.fr/particuliers/vosdroits/F35248",

        category="justice",

        kind="html",

        filename="justice/avocat_proces_penal.txt",

        publisher="service-public.gouv.fr",

    ),

    # --- Procédure et sanctions ---

    SourceSpec(

        id="sp_tribunal_correctionnel",

        title="Déroulement d'une affaire devant le tribunal correctionnel",

        url="https://www.service-public.gouv.fr/particuliers/vosdroits/F1485",

        category="justice",

        kind="html",

        filename="justice/tribunal_correctionnel_procedure.txt",

        publisher="service-public.gouv.fr",

    ),

    SourceSpec(

        id="sp_amende_penale",

        title="Amende prononcée par une juridiction pénale",

        url="https://www.service-public.gouv.fr/particuliers/vosdroits/F32803",

        category="justice",

        kind="html",

        filename="justice/amende_penale.txt",

        publisher="service-public.gouv.fr",

    ),

    SourceSpec(

        id="sp_peine_prison_ferme",

        title="Peine de prison ferme et aménagement",

        url="https://www.service-public.gouv.fr/particuliers/vosdroits/F35705",

        category="justice",

        kind="html",

        filename="justice/peine_prison_ferme.txt",

        publisher="service-public.gouv.fr",

    ),

    SourceSpec(

        id="mj_procedure_penale",

        title="Déroulement de la procédure pénale — Ministère de la Justice",

        url="https://www.justice.gouv.fr/justice-france/justice-penale/procedure-penale",

        category="justice",

        kind="html",

        filename="justice/mj_procedure_penale.txt",

        publisher="Ministère de la Justice",

    ),

    SourceSpec(

        id="mj_justice_penale_hub",

        title="Justice pénale — Ministère de la Justice",

        url="https://www.justice.gouv.fr/justice-france/justice-penale",

        category="justice",

        kind="html",

        filename="justice/mj_justice_penale_hub.txt",

        publisher="Ministère de la Justice",

    ),

    # --- Infractions spécifiques ---

    SourceSpec(

        id="sp_vol_escroquerie",

        title="Vol, escroquerie et abus de confiance",

        url="https://www.service-public.gouv.fr/particuliers/vosdroits/F34396",

        category="justice",

        kind="html",

        filename="justice/infractions_vol_escroquerie.txt",

        publisher="service-public.gouv.fr",

    ),

    SourceSpec(

        id="sp_viol_crime",

        title="Viol commis sur une personne majeure",

        url="https://www.service-public.gouv.fr/particuliers/vosdroits/F1526",

        category="justice",

        kind="html",

        filename="justice/crime_viol.txt",

        publisher="service-public.gouv.fr",

    ),

    SourceSpec(

        id="sp_violences",

        title="Violences volontaires et coups et blessures",

        url="https://www.service-public.gouv.fr/particuliers/vosdroits/F1520",

        category="justice",

        kind="html",

        filename="justice/infractions_violences.txt",

        publisher="service-public.gouv.fr",

    ),

    SourceSpec(

        id="sp_casier_judiciaire",

        title="Casier judiciaire — bulletin n°1, n°2, n°3",

        url="https://www.service-public.gouv.fr/particuliers/vosdroits/F1410",

        category="justice",

        kind="html",

        filename="justice/casier_judiciaire.txt",

        publisher="service-public.gouv.fr",

    ),

    SourceSpec(

        id="sp_justice_mineurs",

        title="Justice pénale des mineurs",

        url="https://www.service-public.gouv.fr/particuliers/vosdroits/F1837",

        category="justice",

        kind="html",

        filename="justice/justice_penale_mineurs.txt",

        publisher="service-public.gouv.fr",

    ),

    # --- Institutions ---

    SourceSpec(

        id="cc_decisions_jurisprudence",

        title="Conseil constitutionnel — décisions et jurisprudence",

        url="https://www.conseil-constitutionnel.fr/decisions",

        category="justice",

        kind="html",

        filename="justice/conseil_constitutionnel_decisions.txt",

        publisher="Conseil constitutionnel",

    ),

    SourceSpec(

        id="data_gouv_justice",

        title="data.gouv.fr — jeux de données Justice",

        url="https://www.data.gouv.fr/fr/organizations/ministere-de-la-justice/",

        category="justice",

        kind="html",

        filename="justice/datagouv_ministere_justice.txt",

        publisher="data.gouv.fr",

    ),

]

