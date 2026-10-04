# Google Cloud Platform (GCP) & Firebase Production Deployment Guide

This guide details the exact, battle-tested production deployment runbook for **Tathvyn** using **Google Cloud Run (Backend)** + **Firebase Hosting (Frontend CDN)** + **Google Secret Manager (Encrypted Credentials)**.

---

## 🏛️ Architecture Overview

```
                         [User Browser]
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
       Static Assets (HTML/JS/CSS)       API Calls & SSE Stream
               │                               │
               ▼                               ▼
 [Firebase Hosting (Global Edge CDN)] [Google Cloud Run]
  https://tathvyn-production.web.app   https://tathvyn-backend-906432301218.us-central1.run.app
  ├── / (SPA Claim Studio)             ├── /api/v1/health (Health check)
  └── /404.html (Edge Fallback Card)   ├── /api/v1/verify (REST verification)
               │                       └── /api/v1/verify/stream (SSE pipeline stream)
       Instant edge delivery                   │
       Automated health diagnostic             ▼
                                     [Google Secret Manager]
                                       ├── GEMINI_API_KEY (gemini-3.8-flash & Google Search Grounding)
                                       └── TAVILY_API_KEY (Tavily search provider)
```

* **Frontend**: Hosted on Firebase Hosting (Google's Global Edge CDN). Instant page loads, global SSL/TLS certificates, zero cold starts. Includes an active edge fallback page (`404.html`) with an interactive health diagnostic ping.
* **Backend**: Hosted on Google Cloud Run (`tathvyn-backend`). Fully managed container with 2 vCPUs and 4 GB RAM, with 1 warm min-instance to avoid model loading delays.
* **Resilient Multi-Provider Retrieval**:
  1. **Tavily Search API** (with sanitized Bearer token and basic depth)
  2. **Gemini Google Search Grounding** (`gemini-3.8-flash` via `google-genai`), bypassing cloud datacenter IP blocks
  3. **DuckDuckGo Search Provider** (zero-key live web fallback)
  4. **Brave Search Provider**
* **Secrets**: Stored in Google Secret Manager, encrypted at rest, and mounted directly into container memory at runtime.
* **CORS**: Cloud Run permits cross-origin requests directly from `https://tathvyn-production.web.app` with credentials.

---

## 🚀 Step-by-Step Deployment Runbook

### Step 1: Tooling & Authentication

Ensure `gcloud` (Google Cloud SDK) and `firebase-tools` are installed:
```powershell
# Authenticate CLIs
gcloud auth login
firebase login

# Set active project
gcloud config set project tathvyn-production
```

---

### Step 2: Enable Google Cloud APIs

```powershell
gcloud services enable `
  run.googleapis.com `
  artifactregistry.googleapis.com `
  cloudbuild.googleapis.com `
  secretmanager.googleapis.com `
  firebase.googleapis.com `
  firebasehosting.googleapis.com
```

---

### Step 3: Create Artifact Registry & Service Account Permissions

#### 1. Create Docker Repository:
```powershell
gcloud artifacts repositories create tathvyn-repo `
  --repository-format=docker `
  --location=us-central1 `
  --description="Docker repository for Tathvyn"
```

#### 2. Grant Permissions to the Project Service Account:
Cloud Build and Cloud Run run under the compute service account (`PROJECT_NUMBER-compute@developer.gserviceaccount.com`). Grant it the required roles:
```powershell
$SA = "906432301218-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding tathvyn-production --member="serviceAccount:$SA" --role="roles/storage.objectViewer"
gcloud projects add-iam-policy-binding tathvyn-production --member="serviceAccount:$SA" --role="roles/logging.logWriter"
gcloud projects add-iam-policy-binding tathvyn-production --member="serviceAccount:$SA" --role="roles/artifactregistry.writer"
gcloud projects add-iam-policy-binding tathvyn-production --member="serviceAccount:$SA" --role="roles/secretmanager.secretAccessor"
```

---

### Step 4: Store API Secrets in Secret Manager

> [!IMPORTANT]
> Always trim trailing whitespace or newlines when piping keys to Secret Manager. Newlines in authorization headers trigger HTTP 403 / CRLF errors on reverse proxies.

```powershell
# Store Gemini Key
gcloud secrets create gemini-api-key --replication-policy="automatic" 2>$null
"YOUR_GEMINI_API_KEY".Trim() | gcloud secrets versions add gemini-api-key --data-file=- --project tathvyn-production

# Store Tavily Key
gcloud secrets create tavily-api-key --replication-policy="automatic" 2>$null
"YOUR_TAVILY_API_KEY".Trim() | gcloud secrets versions add tavily-api-key --data-file=- --project tathvyn-production
```

---

### Step 5: Build Backend Container with Cloud Build

Cloud Build will package the container and pre-cache Hugging Face model weights (`ms-marco-MiniLM-L-6-v2` and `nli-distilroberta-base`) to eliminate cold-start inference latency:

```powershell
gcloud builds submit backend --tag us-central1-docker.pkg.dev/tathvyn-production/tathvyn-repo/backend:latest
```

---

### Step 6: Deploy Backend to Cloud Run

```powershell
gcloud run deploy tathvyn-backend `
  --image us-central1-docker.pkg.dev/tathvyn-production/tathvyn-repo/backend:latest `
  --region us-central1 `
  --platform managed `
  --allow-unauthenticated `
  --memory 4Gi `
  --cpu 2 `
  --min-instances 1 `
  --set-env-vars "Tathvyn_ENVIRONMENT=production" `
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest,TAVILY_API_KEY=tavily-api-key:latest"
```

* Cloud Run outputs the service URL: `https://tathvyn-backend-906432301218.us-central1.run.app`
* Test health endpoint: `https://tathvyn-backend-906432301218.us-central1.run.app/api/v1/health`

---

### Step 7: Build & Deploy Frontend to Firebase Hosting

#### 1. Build Production Bundle:
```powershell
cd frontend
npm run build
cd ..
```

#### 2. Deploy to Firebase:
```powershell
firebase deploy --only hosting
```

The live web application and edge fallback gateway are instantly live:
- **Application URL**: `https://tathvyn-production.web.app`
- **Fallback Gateway**: `https://tathvyn-production.web.app/404.html`

---

## 🔄 Routine Maintenance Commands

| Action | Command |
| :--- | :--- |
| **Re-deploy Backend** (after Python code changes) | `gcloud builds submit backend --tag us-central1-docker.pkg.dev/tathvyn-production/tathvyn-repo/backend:latest`<br>`gcloud run deploy tathvyn-backend --image us-central1-docker.pkg.dev/tathvyn-production/tathvyn-repo/backend:latest --region us-central1` |
| **Re-deploy Frontend** (after React code changes) | `cd frontend; npm run build; cd ..; firebase deploy --only hosting` |
| **View Live Backend Logs** | `gcloud run services logs tail tathvyn-backend --region us-central1` |
| **Check Cloud Run Health** | `curl -s https://tathvyn-backend-906432301218.us-central1.run.app/api/v1/health` |
| **Clean Obsolete Container Images** | `gcloud artifacts docker images delete IMAGE_PATH@DIGEST --quiet --delete-tags` |
| **Destroy Outdated Secret Versions** | `gcloud secrets versions destroy VERSION --secret=SECRET_NAME --project tathvyn-production --quiet` |
