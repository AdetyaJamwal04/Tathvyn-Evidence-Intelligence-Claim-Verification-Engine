# Tathvyn Frontend: Real-Time Intelligence Dashboard

The frontend of **Tathvyn** is a modern Single-Page Application built with **React 18**, **Vite**, and **Vanilla CSS**. It features a design system with dark mode support, real-time Server-Sent Events (SSE) progress animations, epistemic verdict visualizers, and a two-tier graceful fallback system.

---

## 🏛️ Directory Structure

```
frontend/
├── public/
│   └── 404.html              # Static edge fallback page with automated live health probe
├── src/
│   ├── api/
│   │   └── client.js         # REST API & SSE streaming reader
│   ├── components/
│   │   ├── ErrorBoundary.jsx # React error boundary wrapping the application root
│   │   ├── ErrorFallback.jsx # Interactive diagnostic & query-retention fallback view
│   │   ├── Navbar.jsx        # Brand header & dark mode switch
│   │   ├── SearchSection.jsx # Centered hero, search omnibar, example claim chips
│   │   ├── StreamingProgress.jsx # Live pipeline stage progress indicator
│   │   ├── ResultsView.jsx   # Epistemic verdict headline, confidence bars, citations
│   │   └── ThemeToggle.jsx   # Dark/light theme persistence
│   ├── App.jsx               # Primary layout & state coordinator
│   ├── index.css             # CSS custom properties, tokens, animations
│   └── main.jsx              # React DOM entrypoint with top-level ErrorBoundary
├── .env.example              # Environment variable template
├── .env.production           # Production backend API endpoint
├── index.html                # HTML5 shell
├── package.json              # Dependencies & scripts
└── vite.config.js            # Vite build configuration & API proxy (:8000)
```

---

## 🛡️ Two-Tier Graceful Fallback System

To ensure high availability and prevent blank or broken screens during network interruptions or API downtime, the frontend implements two coordinated fallback tiers:

1. **In-App Error Boundary (`ErrorBoundary.jsx` & `ErrorFallback.jsx`)**:
   - Intercepts uncaught React rendering and runtime exceptions.
   - **Query Retention**: Safely preserves the user's entered claim query and parameters so research context is never lost.
   - **Diagnostic Telemetry**: Displays structured error details, timestamps, and collapsible technical logs.
   - **Live Health Diagnostics**: Features an interactive probe that pings the backend `/api/v1/health` endpoint with a live visual latency indicator.
   - **Actionable Recovery**: Offers one-click retry actions, returning home, or reporting issues.

2. **Static Edge Gateway (`public/404.html`)**:
   - Deployed directly to Firebase Global CDN edge caches.
   - Serves immediately on network partitions, invalid routes, or CDN routing failures.
   - Automatically executes an asynchronous health check against the Cloud Run API on load and displays live system status (online/offline, response latency, and timestamp).

---

## 💻 Running the Frontend Locally

### 1. Install Dependencies
```bash
npm install
```

### 2. Run Local Dev Server
```bash
npm run dev
```
Open `http://localhost:3000/`. API requests are automatically proxied to the local backend at `http://localhost:8000`.

### 3. Production Build
```bash
npm run build
```
Generates optimized, minified bundles into `dist/`.

---

## ☁️ Production Deployment (Firebase Hosting)

The frontend is deployed to **Firebase Hosting** (Google Edge CDN) at:
**[https://tathvyn-production.web.app](https://tathvyn-production.web.app)**

### Build & Deploy:
```powershell
# 1. Build production assets
npm run build

# 2. Deploy to Firebase Hosting (from project root)
cd ..
firebase deploy --only hosting
```
