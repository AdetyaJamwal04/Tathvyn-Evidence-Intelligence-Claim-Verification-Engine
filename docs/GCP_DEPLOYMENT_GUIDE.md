# Google Cloud Platform (GCP) Deployment Guide

This guide details the complete manual deployment procedure for **Tathvyn** using **Option A (Google Cloud Run + Firebase Hosting)**.

---

## Architecture Overview

```
                        [User Browser]
                              │
                              ▼
                [Firebase Hosting (Global CDN)]
                     (https://<project>.web.app)
                              │
         ┌────────────────────┴────────────────────┐
         │ Static Assets                           │ API Requests
         ▼ (/assets/*, /index.html)                ▼ (/api/*)
  [Google Edge CDN]                       [Google Cloud Run]
  (Instant React load)                    (service: tathvyn-backend)
                                          (FastAPI + DeBERTa + PyTorch)
                                                   │
                                                   ▼
                                          [Google Gemini 2.0]
```

- **Frontend**: Hosted on Firebase Hosting (Google's Global CDN). Instant page loads, global SSL, zero cold starts.
- **Backend**: Hosted on Google Cloud Run (`tathvyn-backend`). Fully managed serverless container with 2 vCPUs and 4 GB RAM.
- **Unified Domain (Zero CORS)**: Firebase Hosting automatically rewrites `/api/**` to Cloud Run, meaning both frontend and backend share the exact same domain origin.

---

## Part 1: Prerequisites

1. **Google Cloud Account**: [console.cloud.google.com](https://console.cloud.google.com)
2. **GCP Project**: Create a new project (e.g. `tathvyn-production`).
3. **CLI Tools** (Installed locally):
   - **Google Cloud SDK (`gcloud`)**: [Install guide](https://cloud.google.com/sdk/docs/install)
   - **Firebase CLI**: `npm install -g firebase-tools`
4. Authenticate CLIs:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   firebase login
   ```

---

## Part 2: Deploy the Backend to Cloud Run

### Step 1: Enable Cloud Run & Cloud Build APIs
```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com
```

### Step 2: Deploy the Backend Container
From the repository root, run:
```bash
gcloud run deploy tathvyn-backend \
  --source ./backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --min-instances 1 \
  --timeout 300s \
  --set-env-vars TATHVYN_ENVIRONMENT=production,GEMINI_API_KEY="YOUR_GEMINI_API_KEY",TAVILY_API_KEY="YOUR_TAVILY_API_KEY"
```

> **Why these parameters?**
> - `--memory 4Gi` & `--cpu 2`: Ensures PyTorch, DeBERTa, and Cross-Encoder neural models run with high throughput without out-of-memory errors.
> - `--min-instances 1`: Keeps one container warm 24/7 so model weights remain cached in memory, eliminating cold starts.
> - `--timeout 300s`: Allows deep research queries to complete without HTTP connection drops.

### Step 3: Verify the Backend Service
When Cloud Run finishes, it outputs a URL like:
`https://tathvyn-backend-xxxxxxxx-uc.a.run.app`

Test health endpoint:
```bash
curl -f https://tathvyn-backend-xxxxxxxx-uc.a.run.app/api/v1/health
# Returns: {"status":"healthy", "environment":"production"}
```

---

## Part 3: Deploy the Frontend to Firebase Hosting

### Step 1: Build the React Application
From the repository root:
```bash
cd frontend
npm install
npm run build
cd ..
```
This outputs compiled production assets to `frontend/dist/`.

### Step 2: Associate Firebase Project
In the root directory, create/update `.firebaserc`:
```json
{
  "projects": {
    "default": "YOUR_PROJECT_ID"
  }
}
```
*(Replace `YOUR_PROJECT_ID` with your actual GCP Project ID).*

### Step 3: Verify `firebase.json`
Confirm `firebase.json` at the root matches:
```json
{
  "hosting": {
    "public": "frontend/dist",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "/api/**",
        "run": {
          "serviceId": "tathvyn-backend",
          "region": "us-central1"
        }
      },
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
```

### Step 4: Deploy to Firebase Hosting
```bash
firebase deploy --only hosting
```

---

## Part 4: Testing & Verification

1. Open your new Firebase URL in any browser:
   `https://YOUR_PROJECT_ID.web.app` (or `.firebaseapp.com`)
2. Enter a claim in the search bar:
   *"Chandrayaan-3 confirmed water molecules on the lunar south pole."*
3. Watch the live Server-Sent Events progress stream and verify the final synthesized verdict.

---

## Summary of Maintenance Commands

| Action | Command |
| :--- | :--- |
| **Re-deploy backend after Python code changes** | `gcloud run deploy tathvyn-backend --source ./backend --region us-central1` |
| **Re-deploy frontend after React changes** | `cd frontend && npm run build && cd .. && firebase deploy --only hosting` |
| **View live backend logs** | `gcloud run services logs tail tathvyn-backend --region us-central1` |
| **Check service status** | `gcloud run services describe tathvyn-backend --region us-central1` |
