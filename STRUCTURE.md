# Project Structure

```
gesture-sse-assessment/
│
├── README.md                    # Main documentation
├── requirements.txt             # Python dependencies
├── STRUCTURE.md                 # This file
│
├── main.py                      # 🚀 CLI orchestration (run everything)
│
├── data/
│   ├── generate_users.py        # Generate synthetic event data
│   ├── raw_events.csv           # [Generated] Event-level data
│   ├── user_features.csv        # [Generated] Engineered features
│   ├── user_scores.csv          # [Generated] Scored users
│   └── top_users.csv            # [Generated] Ranked output
│
├── featurize.py                 # ⚙️  Event → User feature pipeline
├── score_rules.py               # 🎯 Rule-based scoring (CORE)
├── explain.py                   # 🔍 Explanation generation
│
├── train_xgb.py                 # 🤖 [Optional] Train ML model
├── score_model.py               # 📊 [Optional] Score with ML
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
| **main.py** | Orchestrate pipeline | `main()` | CLI args | All outputs |

---

### Optional Extensions

| File | Purpose | Why Optional |
|------|---------|--------------|
| **train_xgb.py** | Train learned model | Shows evolution path from rules → ML |
| **score_model.py** | Score with model | Demonstrates same features work for both |

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

[Optional Branch]
featurize.py
    ↓
train_xgb.py       (xgboost, sklearn)
    ↓
score_model.py     (xgboost)
    ↓
explain.py         (xgboost, shap)
```

---

## Quick Reference

### Generate Everything
```bash
python main.py --mode pipeline
```

### Run Individual Steps
```bash
python main.py --mode generate     # Step 1: Synthetic data
python main.py --mode featurize    # Step 2: Features
python main.py --mode score-rules  # Step 3: Score
python main.py --mode rank         # Step 4: Top users
python main.py --mode explain      # Step 5: Analysis
```

### Standalone Usage
```bash
# Each module can run independently
python featurize.py data/raw_events.csv data/user_features.csv
python score_rules.py data/user_features.csv data/user_scores.csv
python explain.py data/user_scores.csv
```

---

## Design Principles

1. **One file, one job** — Each module has a single responsibility
2. **Reusable functions** — Core logic exposed as importable functions
3. **Standalone runnable** — Each file has `if __name__ == "__main__"` block
4. **CLI-friendly** — main.py provides unified interface
5. **Pipeline agnostic** — Features work for rules OR models without changes
