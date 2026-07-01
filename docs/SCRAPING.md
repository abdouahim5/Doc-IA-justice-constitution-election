# Web scraping — Sources officielles France

DocIA télécharge automatiquement les documents publics sur la **Constitution**, les **élections**, la **justice** et le **test civique** depuis les sites gouvernementaux.

## Sources cataloguées

| Site | Contenu |
|------|---------|
| vie-publique.fr | Constitution PDF, guide du bureau de vote, intégration |
| Légifrance | Constitution consolidée, arrêté examen civique 2025 |
| Conseil constitutionnel | Constitution, Déclaration 1789, Charte environnement |
| service-public.fr | Modes d'emploi élections, examen civique, laïcité, droits |
| INSEE | Participation électorale |
| elections.interieur.gouv.fr | Portail + PDF découverts automatiquement |
| **formation-civique.interieur.gouv.fr** | Fiches thématiques, listes officielles questions CSP/CR/naturalisation |
| **immigration.interieur.gouv.fr** | Livret du citoyen, charte droits et devoirs, CIR |
| **data.gouv.fr** | Résultats présidentielle 2022 (France, départements, régions), CSV agrégé |

Fichiers sauvegardés dans : `data/documents/sources_officielles/`  
Test civique : `data/documents/sources_officielles/test_civique/` (+ `fiches_crawlees/` via crawler)  
Données tabulaires : `data/documents/sources_officielles/donnees/`

Un `manifest.json` trace chaque téléchargement (date, URL, erreurs).

## Commandes

```powershell
# Télécharger toutes les sources
python main.py scrape

# Test civique / examen civique uniquement (~30 sources + crawler fiches)
python main.py scrape --category test_civique

# Constitution uniquement
python main.py scrape --category constitution

# Élections uniquement
python main.py scrape --category elections

# Sans crawler formation-civique ni PDF découverts
python main.py scrape --category test_civique --no-discover

# Sans gros CSV (plus rapide)
python main.py scrape --light

# Sans open data data.gouv.fr
python main.py scrape --no-datagouv

# Télécharger + ingérer dans PostgreSQL
python main.py scrape --category test_civique --ingest
```

## Installation Docker (PostgreSQL)

```powershell
# PowerShell administrateur
.\scripts\install_docker.ps1

# Ou via CLI
python main.py docker-install --launch
```

Puis :

```powershell
docker compose up -d
python main.py pg-init
python main.py scrape --ingest
python main.py multi-ask "Que dit l'article 2 ?"
```

## Interface web

**Configuration** → section **Sources officielles** → bouton **Télécharger les sources**.

## Bonnes pratiques

- Délai de 1 seconde entre chaque requête (respect des serveurs publics)
- User-Agent identifié : `DocIA-Scraper/1.0`
- En cas d'échec Légifrance (page dynamique), le PDF vie-publique reste la source principale
- Relancer `scrape` régulièrement pour mettre à jour les textes modifiés

## Dépendances

```
beautifulsoup4
lxml
```

Inclus dans `requirements.txt`.
