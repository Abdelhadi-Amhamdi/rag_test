# (Frensh Version)

# API RAG Multi-Tenant - Documentation

## Démarrage Rapide

### 1. Créer un Environnement Virtuel

```bash
python3 -m venv .venv
```

### 2. Activer l'Environnement Virtuel

```bash
source .venv/bin/activate
```

### 3. Installer les Dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les Variables d'Environnement

Créer un fichier `.env` à la racine du projet :

```env
clientA=tenantA_key
clientB=tenantB_key
GOOGLE_GEMINI_API_KEY=APIKEY_HERE

```

### 4. Démarrer le Backend

```bash
fastapi dev main.py
```

L'API sera disponible sur `http://localhost:8000`

### 5. Démarrer l'Interface

```bash
streamlit run app.py
```

L'interface s'ouvrira automatiquement dans votre navigateur sur `http://localhost:8501`

## Tester la Séparation des Clients

### Via l'Interface Streamlit

1. Ouvrir l'application Streamlit
2. Sélectionner **"Client A"** ou **"Client B"** dans le menu déroulant
3. Poser des questions spécifiques aux documents de chaque client
4. Observer que les réponses sont strictement limitées aux données du client sélectionné

### Via cURL (Test de l'API)

**Client A :**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: tenantA_key" \
  -d '{"message": "Comment déclarer un sinistre ?"}'
```

**Client B :**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: tenantB_key" \
  -d '{"message": "Quelle est la procédure de résiliation ?"}'
```

**Test avec Clé Invalide (devrait retourner 401) :**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: invalid_key" \
  -d '{"message": "Test"}'
```

## Approche Technique

### Vue d'Ensemble de l'Architecture

Cette application implémente un système **RAG (Retrieval-Augmented Generation)** avec isolation stricte des données multi-tenant.

### 1. Traitement et Indexation des Documents

**Découpage Sémantique :**

- Les documents sont divisés par détection de phrases via regex (`re.split(r'(?<=[.!?])\s+', text)`)
- Maximum 3 phrases par chunk pour équilibrer précision et coût
- Les petits documents de test produisent des chunks très ciblés

**Génération des Embeddings :**

- Modèle : Google Gemini `gemini-embedding-001`
- Traitement par batch pour l'efficacité

**Normalisation Vectorielle :**

- Normalisation L2 appliquée à tous les embeddings : `embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)`
- Permet de calculer la similarité cosinus comme simple produit scalaire
- Améliore les performances et la stabilité numérique

**Stockage :**

- ChromaDB avec stockage persistant
- Métadonnées incluant : texte original, nom du client
- Métrique de distance : similarité cosinus

### 2. Pipeline de Traitement des Requêtes

**Étape 1 : Embedding de la Requête**

- Génération de l'embedding pour la requête utilisateur avec le même modèle
- Application de la même normalisation L2 pour cohérence

**Étape 2 : Recherche Sémantique**

- Recherche par similarité cosinus dans ChromaDB
- Filtrage par métadonnées du client authentifié
- Récupération des 4 chunks les plus pertinents

**Étape 3 : Authentification et Autorisation**

- Le middleware HTTP valide l'en-tête `X-API-KEY`
- Associe les clés API aux identifiants clients (tenantA, tenantB)
- Rejette les requêtes non autorisées avec statut 401
- Le nom du client n'est jamais exposé dans le corps de la requête

### 3. Génération de Réponse

**Configuration du LLM :**

- Modèle : `gemini-1.5-flash-latest`
- Température : `0.3` (basse pour réduire les hallucinations)
- Top-p : `0.90` (nucleus sampling)
- Top-k : `10` (assure une sélection de tokens de haute qualité)

**Prompt Système :**

- Impose une adhésion stricte au contexte fourni
- Interdit l'invention d'informations
- Exige la citation des sources
- Gère gracieusement les cas "pas de réponse disponible"

**Formatage du Contexte :**

- Chunks récupérés formatés avec scores de pertinence
- Métadonnées sources incluses pour traçabilité
- Contexte complet fourni au LLM

**Réponse :**

- Réponse générée uniquement basée sur le contexte
- Documents sources cités
- Score de confiance calculé à partir des métriques de similarité
- Réponse JSON structurée avec réponse, sources et métadonnées

### 4. Sécurité et Isolation des Données

**Garanties Multi-Tenant :**

- Identification client basée sur clé API
- Filtrage côté serveur par métadonnées client
- Aucune fuite de données inter-client possible
- Le middleware impose l'authentification sur toutes les routes protégées

### 5. Optimisations et Améliorations Futures

**Compromis de l'Implémentation Actuelle :**
La solution actuelle privilégie la simplicité et la rapidité de développement dans le cadre du temps imparti (4-6 heures). Les améliorations suivantes augmenteraient significativement les performances en production :

- Découpage Avancé des Documents
- Recherche Hybride : BM25 + Recherche Sémantique
- Génération Multi-Requêtes

---

# (English Version)

# Multi-Tenant RAG API - Documentation

## Quick Start

### 1. Create Virtual Environment

```bash
python3 -m venv .venv
```

### 2. Activate Virtual Environment

```bash
source .venv/bin/activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
clientA=tenantA_key
clientB=tenantB_key
GOOGLE_GEMINI_API_KEY=APIKEY_HERE

```

### 1. Start the Backend

```bash
fastapi dev main.py
```

The API will be available at `http://localhost:8000`

### 2. Start the Interface

```bash
streamlit run app.py
```

The interface will open automatically in your browser at `http://localhost:8501`

## Testing Client Separation

### Using the Streamlit Interface

1. Open the Streamlit app
2. Select **"Client A"** or **"Client B"** from the dropdown menu
3. Ask questions specific to each client's documents
4. Observe that responses are strictly limited to the selected client's data

### Using cURL (API Testing)

**Client A:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: tenantA_key" \
  -d '{"message": "Comment déclarer un sinistre ?"}'
```

**Client B:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: tenantB_key" \
  -d '{"message": "Quelle est la procédure de résiliation ?"}'
```

**Test Invalid Key (should return 401):**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: invalid_key" \
  -d '{"message": "Test"}'
```

## Technical Approach

### Architecture Overview

This application implements a **Retrieval-Augmented Generation (RAG)** system with strict multi-tenant data isolation.

### 1. Document Processing & Indexing

**Semantic Chunking:**

- Documents are split using regex-based sentence detection (`re.split(r'(?<=[.!?])\s+', text)`)
- Maximum 3 sentences per chunk to balance precision and cost
- Small test documents result in highly focused chunks

**Embedding Generation:**

- Model: Google Gemini `gemini-embedding-001`
- Batch processing for efficiency

**Vector Normalization:**

- L2 normalization applied to all embeddings: `embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)`
- Enables cosine similarity to be computed as simple dot product
- Improves performance and numerical stability

**Storage:**

- ChromaDB with persistent storage
- Metadata includes: original text, client name
- Distance metric: cosine similarity

### 2. Query Processing Pipeline

**Step 1: Query Embedding**

- Generate embedding for user query using the same model
- Apply identical L2 normalization for consistency

**Step 2: Semantic Search**

- Cosine similarity search in ChromaDB
- Filter by authenticated client's metadata
- Retrieve top 4 most relevant chunks

**Step 3: Authentication & Authorization**

- HTTP middleware validates `X-API-KEY` header
- Maps API keys to client identifiers (tenantA, tenantB)
- Rejects unauthorized requests with 401 status
- Client name never exposed in request body

### 3. Answer Generation

**LLM Configuration:**

- Model: `gemini-1.5-flash-latest`
- Temperature: `0.3` (low to reduce hallucinations)
- Top-p: `0.90` (nucleus sampling)
- Top-k: `10` (ensures high-quality token selection)

**System Prompt:**

- Enforces strict adherence to provided context
- Prohibits information invention
- Requires source citation
- Handles "no answer available" cases gracefully

**Context Formatting:**

- Retrieved chunks formatted with relevance scores
- Source metadata included for traceability
- Complete context provided to LLM

**Response:**

- Generated answer based solely on context
- Source documents cited
- Confidence score computed from similarity metrics
- Structured JSON response with answer, sources, and metadata

### 4. Security & Data Isolation

**Multi-Tenant Guarantees:**

- API key-based client identification
- Server-side filtering by client metadata
- No cross-client data leakage possible
- Middleware enforces authentication on all protected routes

### 5. Future Optimizations & Improvements

**Current Implementation Trade-offs:**
The current solution prioritizes simplicity and speed of development for the assignment timeframe (4-6 hours). The following enhancements would significantly improve production performance:

- Advanced Document Chunking
- Hybrid Search: BM25 + Semantic Search
- Multi-Query Generation
