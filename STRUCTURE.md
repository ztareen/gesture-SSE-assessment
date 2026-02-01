# Project Structure

```
gesture-sse-assessment/
│
├── README.md                    # Main documentation
├── requirements.txt             # Python dependencies
├── STRUCTURE.md                 # This file
│
├── main.py                      # CLI orchestration (run everything + web server)
├── server.py                    # Web server for browser-based results dashboard
├── results.html                 # Standalone HTML dashboard (fallback)
│
├── data/
│   ├── generate_users.py        # Generate synthetic event data
│   ├── raw_events.csv           # [Generated] Event-level data
│   ├── user_features.csv        # [Generated] Engineered features
│   ├── user_scores.csv          # [Generated] Scored users
│   └── top_users.csv            # [Generated] Ranked output
│
├── featurize.py                 # Event → User feature pipeline
├── score_rules.py               # Rule-based scoring (CORE)
├── explain.py                   # Explanation generation
│
├── train_xgb.py                 # [Optional] Train ML model
├── score_model.py               # [Optional] Score with ML
│
├── frontend/                    # [Optional] React frontend
│   ├── package.json
│   ├── index.html
│   └── src/
│       ├── App.jsx              # Main React component with data fetching
│       └── main.jsx             # React entry point
│
└── models/                      # [Optional] Trained model artifacts
    ├── xgb_model.json
    └── training_metrics.json
```

---

## File Responsibilities

### Core Pipeline (Required for Option C)

| File | Purpose | Key Functions | Input | Output |
|------|---------|---------------|-------|--------|
| **generate_users.py** | Generate synthetic data | `generate_events()` | — | `raw_events.csv` |
| **featurize.py** | Build user features | `build_user_features()`<br>`write_user_features()` | `raw_events.csv` | `user_features.csv` |
| **score_rules.py** | Score with rules | `score_users_rules()` | `user_features.csv` | `user_scores.csv` |
| **explain.py** | Generate explanations | `explain_rules_global()`<br>`explain_rules_local()` | `user_scores.csv` | Console output |
| **main.py** | Orchestrate pipeline + web server | `main()`<br>`run_pipeline()`<br>`start_web_server()` | CLI args | All outputs + web dashboard |
| **server.py** | Web server & API | `start_server()`<br>API endpoints: `/api/summary`, `/api/top-users`, `/api/distribution` | CSV files | JSON API + HTML dashboard |

---

### Optional Extensions

| File | Purpose | Why Optional |
|------|---------|--------------|
| **train_xgb.py** | Train learned model | Shows evolution path from rules → ML |
| **score_model.py** | Score with model | Demonstrates same features work for both |
| **frontend/** | React web dashboard | Visual interface for viewing results (also served via `results.html`) |
| **results.html** | Standalone HTML dashboard | Simple fallback dashboard that works without React build |

---

## Data Flow

```
Raw Events (100 users, ~500-1000 events)
    ↓
[featurize.py]
    ↓
User Features (100 rows, ~30 columns)
    ↓
[score_rules.py]  ←──────┐
    ↓                     │
User Scores              │ (Alternative path)
    ↓                     │
[main.py --mode rank]    │
    ↓                     │
Top Users (top 20)       │
    ↓                     │
[server.py]              │
    ↓                     │
Web Dashboard            │
(http://localhost:8000)  │
                          │
                    [train_xgb.py]
                          ↓
                    XGBoost Model
                          ↓
                    [score_model.py]
                          ↓
                    Model Scores
```

---

## Module Dependencies

```
generate_users.py  (no dependencies)
    ↓
featurize.py       (pandas, numpy)
    ↓
score_rules.py     (pandas, numpy, json, math)
    ↓
explain.py         (pandas, json)
    ↓
main.py            (all above + argparse)
    ↓
server.py          (flask, flask-cors, pandas, webbrowser)

[Optional Branch]
featurize.py
    ↓
train_xgb.py       (xgboost, sklearn)
    ↓
score_model.py     (xgboost)
    ↓
explain.py         (xgboost, shap)

[Web Interface]
server.py
    ↓
results.html        (standalone, no dependencies)
    OR
frontend/           (React + Vite, npm dependencies)
```

---

## Quick Reference

### Generate Everything (with Web Dashboard)
```bash
py main.py --mode pipeline
```
This will:
1. Run the complete pipeline (generate → featurize → score → rank → explain)
2. Start a web server on http://localhost:8000
3. Automatically open your browser to view results

### Run Individual Steps
```bash
py main.py --mode generate     # Step 1: Synthetic data
py main.py --mode featurize    # Step 2: Features
py main.py --mode score-rules  # Step 3: Score
py main.py --mode rank         # Step 4: Top users
py main.py --mode explain      # Step 5: Analysis
```

### Standalone Usage
```bash
# Each module can run independently
py featurize.py data/raw_events.csv data/user_features.csv
py score_rules.py data/user_features.csv data/user_scores.csv
py explain.py data/user_scores.csv
```

### Web Server (Standalone)
```bash
# Start server manually (after pipeline has run)
py server.py
# Then visit http://localhost:8000
```

### Frontend Development (Optional)
```bash
cd frontend
npm install
npm run dev
# React dev server runs on separate port (usually :5173)
```

---

## Design Principles

1. **One file, one job** — Each module has a single responsibility
2. **Reusable functions** — Core logic exposed as importable functions
3. **Standalone runnable** — Each file has `if __name__ == "__main__"` block
4. **CLI-friendly** — main.py provides unified interface
5. **Pipeline agnostic** — Features work for rules OR models without changes
6. **Dual output** — Results displayed in both terminal and browser dashboard
7. **Windows-friendly** — Uses `py` command for cross-platform compatibility

## Web Server & API

The `server.py` module provides:

- **API Endpoints:**
  - `GET /api/summary` - Summary statistics (total users, mean/median scores, intent distribution)
  - `GET /api/top-users` - Top 20 users by score
  - `GET /api/distribution` - Score distribution by ranges
  - `GET /api/users` - All users data

- **Web Interface:**
  - Serves `results.html` (standalone dashboard) or built React frontend
  - Automatically opens browser when pipeline completes
  - Auto-refreshes data every 5 seconds

- **Dependencies:**
  - Flask (web framework)
  - flask-cors (CORS support for API)
  - pandas (CSV reading)
  - webbrowser (auto-open browser)