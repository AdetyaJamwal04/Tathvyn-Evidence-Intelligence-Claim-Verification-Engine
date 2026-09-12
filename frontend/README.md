# Tathvyn Frontend: Real-Time Intelligence Dashboard

The frontend of **Tathvyn** is a modern Single-Page Application built with **React 18**, **Vite**, and **Vanilla CSS**. It features a design system with dark mode support, real-time Server-Sent Events (SSE) progress animations, and epistemic verdict visualizers.

---

## 📁 Directory Structure

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
├── index.html                    # HTML5 shell
├── package.json                  # Dependencies & scripts
└── vite.config.js                # Vite build configuration & API proxy (:8000)
```

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
npm install
```

### 2. Run Local Dev Server
```bash
npm run dev
```
Open **`http://localhost:3000`** in your browser.

### 3. Production Build
```bash
npm run build
```
Builds optimized production assets to `frontend/dist/`, which are automatically served by the FastAPI backend in production.
