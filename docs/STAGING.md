# France Civique IA — Staging

> Une question sur la citoyenneté ? **DocIA** répond à partir des sources officielles — Constitution, élections, justice, test civique — avec les textes et les citations.

**Branche :** `main` — environnement de staging à déployer sur Hetzner

---

## Environnement déployé

| | |
|---|---|
| **Serveur** | Hetzner CX22 — Ubuntu 24.04 |
| **IP** | `—` *(à compléter après déploiement)* |
| **Domaine** | `—` *(optionnel — HTTPS via Caddy)* |
| **Stack** | Docker Compose (caddy + app + postgres pgvector) |
| **Statut** | 🟡 En attente de déploiement |

| Interface | URL |
|-----------|-----|
| **Application** | `http://IP_OU_DOMAINE` |
| **France Civique** (multi-agent) | `http://IP_OU_DOMAINE` → menu *France Civique* |
| **Test civique** | `http://IP_OU_DOMAINE` → menu *Test civique* |
| **Health** | `http://IP_OU_DOMAINE/_stcore/health` |

> Avec HTTPS (profil Caddy) : remplacez `http://IP:8501` par `https://votre-domaine.fr`

---

## Déployer / mettre à jour le staging

```bash
# Sur le VPS
git clone https://github.com/VOTRE_USER/docia.git
cd docia
cp .env.production.example .env
nano .env   # OPENAI_API_KEY, POSTGRES_PASSWORD, DOMAIN (si HTTPS)

docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec app python main.py pg-ingest
docker compose -f docker-compose.prod.yml exec app python main.py index
```

**HTTPS :**
```bash
docker compose -f docker-compose.prod.yml --profile https up -d --build
```

**Mise à jour après un `git push` :**
```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

---

## Après déploiement — compléter ce fichier

1. Remplacez `IP_OU_DOMAINE` dans le tableau ci-dessus
2. Changez le statut en 🟢 **En ligne**
3. Mettez à jour la section équivalente dans [`README.md`](../README.md)

Exemple une fois en ligne :

| | |
|---|---|
| **Serveur** | Hetzner CX22 — Ubuntu 24.04 |
| **IP** | `65.109.143.85` |
| **Domaine** | `docia.example.fr` |
| **Stack** | Docker Compose (caddy + app + postgres pgvector) |
| **Statut** | 🟢 En ligne |

| Interface | URL |
|-----------|-----|
| **Application** | https://docia.example.fr |
| **France Civique** | https://docia.example.fr |
| **Test civique** | https://docia.example.fr |
| **Health** | https://docia.example.fr/_stcore/health |

---

## Commandes utiles (VPS)

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f app
docker compose -f docker-compose.prod.yml exec app python main.py pg-stats
```

Guide complet : [DEPLOIEMENT.md](DEPLOIEMENT.md)
