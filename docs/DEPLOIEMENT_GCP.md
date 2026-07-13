# Déploiement GCP — France Civique IA (DocIA)

Guide **pas à pas** pour déployer DocIA sur **Google Cloud Platform** avec une **VM Compute Engine** + Docker Compose.

> **Architecture retenue :** VM Ubuntu + Docker (app Streamlit + PostgreSQL pgvector).  
> C’est la solution la plus simple et compatible avec le projet actuel.

---

## Vue d'ensemble

```
Internet
    │
    ▼
IP externe GCP (firewall : 8501 ou 80/443)
    │
    ▼
VM Compute Engine (e2-medium, Ubuntu 24.04)
    │
    ├── docia-app      (Streamlit :8501)
    ├── docia-postgres (pgvector, réseau interne)
    └── docia-caddy    (HTTPS optionnel)
```

| Composant GCP | Rôle |
|---------------|------|
| **Compute Engine** | VM qui héberge Docker |
| **VPC / Firewall** | Ouvre les ports 8501 (ou 80/443) |
| **IP statique** (optionnel) | Adresse fixe pour le staging |
| **Secret Manager** (optionnel) | Stocker `OPENAI_API_KEY` |

**Coût estimé :** ~25–40 €/mois (e2-medium + disque 50 Go + trafic).

---

## Étape 0 — Prérequis

- [ ] Compte [Google Cloud](https://console.cloud.google.com/) avec **facturation activée**
- [ ] Clé **OpenAI** (`OPENAI_API_KEY`)
- [ ] Dépôt Git : https://github.com/abdouahim5/Doc-IA-justice-constitution-election
- [ ] (Optionnel) [gcloud CLI](https://cloud.google.com/sdk/docs/install) installé sur votre PC

---

## Étape 1 — Créer un projet GCP

### Console web

1. Allez sur https://console.cloud.google.com/
2. Menu **Sélecteur de projet** → **Nouveau projet**
3. Nom : `docia-france-civique`
4. Cliquez **Créer**
5. **Facturation** → associez un compte de facturation au projet

### Ligne de commande (optionnel)

```bash
gcloud projects create docia-france-civique --name="DocIA France Civique"
gcloud config set project docia-france-civique
gcloud billing accounts list
gcloud billing projects link docia-france-civique --billing-account=VOTRE_ID_FACTURATION
```

---

## Étape 2 — Activer les APIs

### Console

**APIs et services** → **Bibliothèque** → activer :

- **Compute Engine API**

### CLI

```bash
gcloud services enable compute.googleapis.com
```

---

## Étape 3 — Créer la VM

### Console (recommandé pour débuter)

1. **Compute Engine** → **Instances de VM** → **Créer une instance**
2. Paramètres :

| Champ | Valeur |
|-------|--------|
| **Nom** | `docia-staging` |
| **Région** | `europe-west9` (Paris) ou `europe-west1` (Belgique) |
| **Type de machine** | `e2-medium` (2 vCPU, 4 Go RAM) |
| **Disque de démarrage** | Ubuntu 24.04 LTS, **50 Go** SSD |
| **Pare-feu** | ☑ Autoriser le trafic HTTP |
| | ☑ Autoriser le trafic HTTPS |

3. **Réseau** → cochez aussi **Autoriser le trafic HTTP/HTTPS** si proposé
4. **Créer**

### CLI

```bash
gcloud compute instances create docia-staging \
  --zone=europe-west9-a \
  --machine-type=e2-medium \
  --image-family=ubuntu-2404-lts-amd64 \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-balanced \
  --tags=http-server,https-server
```

---

## Étape 4 — Règles de pare-feu

### Ouvrir le port Streamlit (8501)

**Console :** **VPC réseau** → **Pare-feu** → **Créer une règle**

| Champ | Valeur |
|-------|--------|
| Nom | `allow-docia-streamlit` |
| Cibles | Toutes les instances du réseau |
| Filtres source | `0.0.0.0/0` (ou votre IP pour plus de sécurité) |
| Protocoles | TCP `8501` |

### CLI

```bash
gcloud compute firewall-rules create allow-docia-streamlit \
  --allow=tcp:8501 \
  --target-tags=http-server \
  --description="DocIA Streamlit"
```

> Les ports **80** et **443** sont déjà ouverts si vous avez coché HTTP/HTTPS à la création de la VM (pour Caddy).

---

## Étape 5 — IP externe (recommandé)

### Console

**VPC réseau** → **Adresses IP** → **Réserver une adresse IP statique** → associez-la à `docia-staging`

### CLI

```bash
gcloud compute addresses create docia-ip --region=europe-west9
gcloud compute instances delete-access-config docia-staging --zone=europe-west9-a --access-config-name="External NAT"
gcloud compute instances add-access-config docia-staging \
  --zone=europe-west9-a \
  --address=$(gcloud compute addresses describe docia-ip --region=europe-west9 --format='value(address)')
```

Notez l’IP : `gcloud compute addresses describe docia-ip --region=europe-west9 --format='value(address)'`

---

## Étape 6 — Se connecter en SSH à la VM

### Console

**Compute Engine** → **Instances** → cliquez **SSH** à côté de `docia-staging`

### Depuis votre PC

```bash
gcloud compute ssh docia-staging --zone=europe-west9-a
```

---

## Étape 7 — Installer Docker sur la VM

Sur la VM (via SSH) :

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
```

**Déconnectez-vous et reconnectez-vous** en SSH pour que le groupe `docker` soit pris en compte.

Vérification :

```bash
docker --version
docker compose version
```

---

## Étape 8 — Cloner le projet

```bash
cd ~
git clone https://github.com/abdouahim5/Doc-IA-justice-constitution-election.git
cd Doc-IA-justice-constitution-election
```

---

## Étape 9 — Configurer les secrets (.env)

```bash
cp .env.production.example .env
nano .env
```

**Obligatoire :**

```env
OPENAI_API_KEY=sk-votre-vraie-cle
POSTGRES_PASSWORD=mot-de-passe-fort-et-unique
EMBEDDING_PROVIDER=openai
LLM_PROVIDER=openai
```

Sauvegarde : `Ctrl+O` → Entrée → `Ctrl+X`

---

## Étape 10 — Lancer le déploiement Docker

### Option A — script automatique

```bash
chmod +x deploy/gcp-vm-setup.sh
./deploy/gcp-vm-setup.sh
```

### Option B — commandes manuelles

```bash
docker compose -f docker-compose.gcp.yml up -d --build
```

Attendre 2–5 minutes (build de l’image). Vérifier :

```bash
docker compose -f docker-compose.gcp.yml ps
docker compose -f docker-compose.gcp.yml logs -f app
```

---

## Étape 11 — Ingérer le corpus (première fois)

```bash
docker compose -f docker-compose.gcp.yml exec app python main.py pg-ingest
docker compose -f docker-compose.gcp.yml exec app python main.py index
```

> L’ingestion peut prendre **30–60 min** (appels API embeddings OpenAI).

Suivre la progression :

```bash
docker compose -f docker-compose.gcp.yml exec app python main.py pg-stats
```

---

## Étape 12 — Tester l'application

Remplacez `IP_EXTERNE` par l’IP de votre VM :

| Interface | URL |
|-----------|-----|
| **Application** | http://IP_EXTERNE:8501 |
| **Health** | http://IP_EXTERNE:8501/_stcore/health |

Sur la VM :

```bash
curl -s http://localhost:8501/_stcore/health
```

---

## Étape 13 — HTTPS avec domaine (optionnel)

1. Achetez un nom de domaine (OVH, Google Domains, etc.)
2. Créez un enregistrement **A** → IP externe de la VM
3. Dans `.env` :

```env
DOMAIN=docia.votre-domaine.fr
ACME_EMAIL=admin@votre-domaine.fr
```

4. Lancez Caddy :

```bash
docker compose -f docker-compose.gcp.yml --profile https up -d
```

Accès : **https://docia.votre-domaine.fr**

---

## Étape 14 — Mettre à jour le README staging

Sur la VM, après déploiement :

```bash
cp deploy/staging.env.example deploy/staging.env
nano deploy/staging.env
```

```env
STAGING_IP=VOTRE_IP_GCP
STAGING_STATUS=en_ligne
STAGING_URL_APP=http://VOTRE_IP_GCP:8501
STAGING_URL_HEALTH=http://VOTRE_IP_GCP:8501/_stcore/health
```

Puis sur votre PC (après `git pull`) :

```bash
py scripts/update_staging_status.py
git add README.md docs/STAGING.md deploy/staging.metrics.json
git commit -m "Staging GCP en ligne"
git push
```

---

## Commandes d'administration (VM)

```bash
# Logs
docker compose -f docker-compose.gcp.yml logs -f app

# Redémarrer
docker compose -f docker-compose.gcp.yml restart app

# Mise à jour après git push
git pull
docker compose -f docker-compose.gcp.yml up -d --build

# Stats corpus
docker compose -f docker-compose.gcp.yml exec app python main.py pg-stats

# Vider cache
docker compose -f docker-compose.gcp.yml exec app python main.py pg-cache-clear

# Arrêter
docker compose -f docker-compose.gcp.yml down
```

---

## Sécurité GCP — bonnes pratiques

| Recommandation | Détail |
|----------------|--------|
| **Ne pas exposer Postgres** | `docker-compose.gcp.yml` : Postgres en réseau interne uniquement |
| **Restreindre le pare-feu** | Limiter `8501` à votre IP au lieu de `0.0.0.0/0` |
| **Secrets** | Ne jamais committer `.env` ; utiliser [Secret Manager](https://cloud.google.com/secret-manager) en prod |
| **IAM** | Compte de service dédié si vous automatisez |
| **Sauvegardes** | Snapshot du disque VM ou export volume `pgdata` |

### Secret Manager (avancé)

```bash
echo -n "sk-..." | gcloud secrets create openai-api-key --data-file=-
```

Puis injecter dans `.env` au démarrage via script — voir doc Google Secret Manager.

---

## Dépannage

| Problème | Solution |
|----------|----------|
| Page inaccessible | Vérifier règle pare-feu TCP 8501 + `docker ps` |
| `app` redémarre | `docker logs docia-app` — vérifier `OPENAI_API_KEY` |
| Build échoue (disque) | Augmenter disque VM à 80 Go |
| Corpus vide | Relancer `pg-ingest` |
| HTTPS échoue | DNS propagé ? Ports 80/443 ouverts ? |

---

## Récapitulatif des fichiers GCP

| Fichier | Rôle |
|---------|------|
| `docker-compose.gcp.yml` | Stack production GCP |
| `deploy/gcp-vm-setup.sh` | Installation automatique sur VM |
| `deploy/gcp.env.example` | Modèle variables GCP |
| `requirements.docker.txt` | Image légère (sans PyTorch) |
| `Dockerfile` | Image `docia-app` |

---

## Alternative GCP (non couverte ici)

| Option | Quand l'utiliser |
|--------|------------------|
| **Cloud Run + Cloud SQL** | Serverless, plus complexe (pgvector sur Cloud SQL) |
| **GKE** | Fort trafic, équipe DevOps |
| **Vertex AI** | Si migration vers Gemini |

Pour ce projet, **Compute Engine + Docker** reste le choix recommandé.

---

Voir aussi : [DEPLOIEMENT.md](DEPLOIEMENT.md) · [STAGING.md](STAGING.md) · [CONFIGURATION.md](CONFIGURATION.md)
