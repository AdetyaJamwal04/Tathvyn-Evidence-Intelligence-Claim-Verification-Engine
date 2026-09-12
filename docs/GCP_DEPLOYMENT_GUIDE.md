# Google Cloud Platform (GCP) & Firebase Production Deployment Guide

This guide details the exact, battle-tested production deployment runbook for **Tathvyn** using **Google Cloud Run (Backend)** + **Firebase Hosting (Frontend CDN)** + **Google Secret Manager (Encrypted Credentials)**.

---

## 🏗️ Architecture Overview

```
                         [User Browser]
                               │
               ┌───────────────┴───────────────┐
               │                               │
       Static Assets (HTML/JS/CSS)       API Calls & SSE Stream
               │                               │
               ▼                               ▼
 [Firebase Hosting (Global CDN)]     [Google Cloud Run]
  https://tathvyn-production.web.app  https://tathvyn-backend-906432301218.us-central1.run.app
               │                               │
       Instant edge delivery           FastAPI + PyTorch + DeBERTa
       Zero cold starts                (2 vCPU, 4 GiB RAM, 1 warm instance)
                                               │
                                               ▼
                                      [Google Secret Manager]
                                      • GEMINI_API_KEY (Gemini 2.0 Flash)
                                      • TAVILY_API_KEY (Web Search)
```

* **Frontend**: Hosted on Firebase Hosting (Google's Global Edge CDN). Instant page loads, global SSL/TLS certificates, zero cold starts.
* **Backend**: Hosted on Google Cloud Run (`tathvyn-backend`). Fully managed container with 2 vCPUs and 4 GB RAM, with 1 warm min-instance to avoid model loading delays.
* **Secrets**: Stored in Google Secret Manager, encrypted at rest, and mounted directly into container memory at runtime.
* **CORS**: Cloud Run permits cross-origin requests directly from `https://tathvyn-production.web.app` with credentials.

---

## 🛠️ Step-by-Step Deployment Runbook

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
In modern GCP projects, Cloud Build and Cloud Run run under the compute service account (`PROJECT_NUMBER-compute@developer.gserviceaccount.com`). Grant it the required roles:
```powershell
$SA = "906432301218-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding tathvyn-production --member="serviceAccount:$SA" --role="roles/storage.objectViewer"
gcloud projects add-iam-policy-binding tathvyn-production --member="serviceAccount:$SA" --role="roles/logging.logWriter"
gcloud projects add-iam-policy-binding tathvyn-production --member="serviceAccount:$SA" --role="roles/artifactregistry.writer"
gcloud projects add-iam-policy-binding tathvyn-production --member="serviceAccount:$SA" --role="roles/secretmanager.secretAccessor"
```

---

### Step 4: Store API Secrets in Secret Manager

```powershell
# Store Gemini Key
gcloud secrets create gemini-api-key --replication-policy="automatic" 2>$null
Set-Content -Path "$env:TEMP\gemini_key.txt" -Value "YOUR_GEMINI_API_KEY" -NoNewline
gcloud secrets versions add gemini-api-key --data-file="$env:TEMP\gemini_key.txt"
Remove-Item "$env:TEMP\gemini_key.txt"

# Store Tavily Key
gcloud secrets create tavily-api-key --replication-policy="automatic" 2>$null
Set-Content -Path "$env:TEMP	avily_key.txt" -Value "YOUR_TAVILY_API_KEY" -NoNewline
gcloud secrets versions add tavily-api-key --data-file="$env:TEMP	avily_key.txt"
Remove-Item "$env:TEMP	avily_key.txt"
```

---

### Step 5: Build Backend Container with Cloud Build

Ensure `backend/.gcloudignore` excludes the local virtualenv:
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

#### 1. Set Production API URL in Frontend:
```powershell
Set-Content -Path "frontend\.env.production" -Value "VITE_API_URL=https://tathvyn-backend-906432301218.us-central1.run.app"
```

#### 2. Build Production Bundle:
```powershell
cd frontend
npm run build
cd ..
```

#### 3. Deploy to Firebase:
```powershell
firebase deploy --only hosting
```

---

## 🔄 Routine Maintenance Commands

| Action | Command |
| :--- | :--- |
| **Re-deploy Backend** (after Python code changes) | `gcloud builds submit backend --tag us-central1-docker.pkg.dev/tathvyn-production/tathvyn-repo/backend:latest`<br>`gcloud run deploy tathvyn-backend --image us-central1-docker.pkg.dev/tathvyn-production/tathvyn-repo/backend:latest --region us-central1` |
| **Re-deploy Frontend** (after React code changes) | `cd frontend; npm run build; cd ..; firebase deploy --only hosting` |
| **View Live Backend Logs** | `gcloud run services logs tail tathvyn-backend --region us-central1` |
| **Check Cloud Run Health** | `curl -s https://tathvyn-backend-906432301218.us-central1.run.app/api/v1/health` |
