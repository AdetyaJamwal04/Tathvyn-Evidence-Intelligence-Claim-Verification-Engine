# Tathvyn Frontend: Real-Time Intelligence Dashboard

The frontend of **Tathvyn** is a modern Single-Page Application built with **React 18**, **Vite**, and **Vanilla CSS**. It features a design system with dark mode support, real-time Server-Sent Events (SSE) progress animations, and epistemic verdict visualizers.

---

## 🏗️ Directory Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── client.js             # REST API & SSE streaming reader
│   ├── components/
│   │   ├── Navbar.jsx            # Brand header & dark mode switch
│   │   ├── SearchSection.jsx     # Centered hero, search omnibar, example claim chips
│   │   ├── StreamingProgress.jsx # Live pipeline stage progress indicator
│   │   ├── ResultsView.jsx       # Epistemic verdict headline, confidence bars, citations
│   │   └── ThemeToggle.jsx       # Dark/light theme persistence
│   ├── App.jsx                   # Primary layout & state coordinator
│   ├── index.css                 # CSS custom properties, tokens, animations
│   └── main.jsx                  # React DOM entrypoint
├── .env.example                  # Environment variable template
├── index.html                    # HTML5 shell
├── package.json                  # Dependencies & scripts
└── vite.config.js                # Vite build configuration & API proxy (:8000)
```

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

---

## ☁️ Production Deployment (Firebase Hosting)

The frontend is deployed to **Firebase Hosting** (Google Edge CDN) at:
**[https://tathvyn-production.web.app](https://tathvyn-production.web.app)**

### Build & Deploy:
```powershell
# 1. Set backend API URL
Set-Content -Path "frontend\.env.production" -Value "VITE_API_URL=https://tathvyn-backend-906432301218.us-central1.run.app"

# 2. Build production assets
npm run build

# 3. Deploy to Firebase (from project root)
cd ..
firebase deploy --only hosting
```
