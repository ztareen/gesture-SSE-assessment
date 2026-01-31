# Gesture SSE Assessment — Scoring / Ranking Slice

## Overview

Based off of the instructions that I was given, I created a project that does the following:

1. Creates and reads a dataset of synthetic user interaction events including page views, pricing page visits, demo requests, signups, and calendar bookings
2. Identifies the users with high intent and who will have a high clickthrough rate based on important parameters
3. Outputs a "score" from 1-100 that will indicate and reflect their actual interactiveness and if we can consider the user "high intent"
4. Each score, once assigned, is clearly explained
5. Parameters are set using existing guidelines

Overall, the project is designed based on the following parameters which were noted as priorities in the given README:

- Everything is explainable, traceable, and can be easily broken down if things are going wrong or need adjustment
- The project is meant to actually mirror genuine product and user analysis from relevant platforms like Gesture
- Data is all formatted in a real format that reflects the type of information that we can realistically get without breaching privacy (i.e. location and demographic information but not things like IP address or information that could be flagged as potentially stolen)
- The features, weights for different parameters coefficients, and overall logic of how all the programs can work together are easily editable

---

## The Pipeline

The way that all this code works together is that you create the "user events", which creates a CSV (`data/raw_events.csv`). From there, we extrapolate the features (`featurize.py` creates `data/user_features.csv`), and produce the score and explanation (`score_rules.py` creates `data/user_scores.csv`).

For user convenience, everything can be run with just `main.py`.

At a high level, the pipeline looks like this:

> **Synthetic events** → **sessions** → **users** → **features** → **score + explanation**

---

## Architecture

The code is split into separate modules where each file does one thing. This makes it way easier to debug and change individual pieces without breaking everything else. The core scoring logic lives in `score_rules.py` and uses configurable weights, so you can tweak what matters most without rewriting code.

### Core Modules (Required)

#### `data/generate_users.py`
Generates realistic event-level interaction data for ~100 users:
- Page views, pricing views, demo requests, signups, calendar bookings
- Repeat sessions, bounces, and spammy behavior
- User context (location, device, account balance, browsing history)

**Output:** `data/raw_events.csv`

#### `featurize.py`
Aggregates raw events into structured user-level features.

**Key functions:**
- `build_user_features(raw_events_path)` → DataFrame
- `write_user_features(user_df, output_path)`

**Session-level aggregation:**  
Prevents double-counting bounces/spam across multiple events

**User-level features:**
- **Funnel actions:** signups, calendar bookings, demo clicks
- **Engagement:** repeat session rate, page views, recency
- **Context:** account balance, browsing depth
- **Label:** `converted` = 1 if signup + booking, else 0

**Output:** `data/user_features.csv`

#### `score_rules.py` (Core Deliverable)
**The explainable scoring model** — assigns each user:

1. **Score** from 0–100
2. **Label** (high, medium, low)
3. **Explanation** showing top contributing signals
4. **Feature contributions** (JSON breakdown)

**Key function:**
```python
score_users_rules(user_df, weights=None, thresholds=None) → DataFrame
```

**Scoring logic:**
- Weighted, normalized features (configurable via `DEFAULT_WEIGHTS`)
- High-intent actions (signups, bookings) dominate
- Mid-funnel signals (demos, pricing views) matter
- Engagement and context provide boosts
- Recency bonus for recent activity

> Every score is decomposable into per-feature contribution points.

**Output:** `data/user_scores.csv`

#### `explain.py`
Unified explanation module for both rules and models.

**Key functions:**
- `explain_rules_global(scored_df)` — Dataset-wide insights
- `explain_rules_local(scored_df, user_id)` — Individual user deep-dive
- `explain_model_global(model_path)` — XGBoost feature importance
- `explain_model_local(model_path, features, user_id)` — SHAP values

#### `main.py`
Orchestration script with CLI for running the entire pipeline or individual components.

**Usage:**
```bash
# Run complete pipeline
python main.py --mode pipeline

# Run individual steps
python main.py --mode generate --n-users 100
python main.py --mode featurize
python main.py --mode score-rules
python main.py --mode rank --n 20
python main.py --mode explain

# Explain specific user
python main.py --mode explain --user-id user_001
```

---

## This code is useful for experimentation as well

You can use this scoring system to find their engagement levels and identify targeted groups where you run experiments. For example, you have 100 users and you run the experiment on 50 and have a control group of 50. The scoring system helps you stratify users by intent level so your experiments have balanced groups and meaningful results.

---

## XGBoost

I also included optional XGBoost training files (`train_xgb.py` and `score_model.py`) to show how you can evolve from rule-based scoring to machine learning using the exact same features. The same feature pipeline works for both approaches without any modifications.

### Optional Modules (Evolution Path)

#### `train_xgb.py`
Train an XGBoost classifier on user features.

```bash
python train_xgb.py --input data/user_features.csv --output models/xgb_model.json
```

Outputs:
- Trained model (`models/xgb_model.json`)
- Training metrics (`models/training_metrics.json`)
- Feature importance analysis

#### `score_model.py`
Score users using trained XGBoost model instead of rules.

```bash
python score_model.py --features data/user_features.csv --model models/xgb_model.json --compare
```

The `--compare` flag shows side-by-side rule vs. model score comparison.

---

## Why This Approach?

| **Principle** | **Rationale** |
|--------------|---------------|
| **Explainability first** | Avoids black-box scoring — always clear why one user ranks above another |
| **Modular design** | Each file has one job → easy to test, debug, extend |
| **Session → user separation** | Prevents inflated metrics, mirrors real analytics pipelines |
| **Simple but realistic** | Small codebase, production-inspired structure |
| **Rules → ML ready** | Same features work for both approaches without modification |

---

## Step by Step Instructions to Start and Run the Entire Project

### Installation

```bash
pip install -r requirements.txt
```

### Run Complete Pipeline

```bash
python main.py --mode pipeline
```

This will:
1. Generate synthetic event data
2. Build user features
3. Score users with rule-based model
4. Generate ranked list of top users
5. Print global explanations

### Step-by-Step

```bash
# 1. Generate data
python main.py --mode generate --n-users 100

# 2. Build features
python main.py --mode featurize

# 3. Score users
python main.py --mode score-rules

# 4. Rank and export top users
python main.py --mode rank --n 20

# 5. Explain results
python main.py --mode explain
python main.py --mode explain --user-id user_042  # specific user
```

### Optional: Train ML Model

```bash
# Train XGBoost
python train_xgb.py

# Score with model
python score_model.py --compare

# Explain model
python explain.py --model models/xgb_model.json
```

---

## Output Files

```
data/
├── raw_events.csv          # Synthetic event-level data
├── user_features.csv       # Engineered user features
├── user_scores.csv         # Scored + explained users (rules)
├── top_users.csv          # Top N ranked users for downstream use
└── user_model_scores.csv  # (Optional) Model-based scores

models/
├── xgb_model.json         # (Optional) Trained XGBoost model
└── training_metrics.json  # (Optional) Training performance
```

---

## What Comes Next?

### Short-term improvements:
- Add more behavioral signals (time-on-page, scroll depth)
- Implement collaborative filtering for "users like you"
- A/B test different weight configurations

### Medium-term evolution:
- Online learning with feedback loop (did sales convert them?)
- Multi-objective scoring (intent + fit + urgency)
- Real-time scoring API

### Production deployment:
- Feature store for consistent feature computation
- Model monitoring and drift detection
- Scheduled batch scoring + incremental updates

---

<div align="center">

**Built with clarity, designed for scale**

</div>
