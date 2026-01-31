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

---

## Architecture

The code is split into separate modules where each file does one thing. This makes it way easier to debug and change individual pieces without breaking everything else. The core scoring logic lives in `score_rules.py` and uses configurable weights, so you can tweak what matters most without rewriting code.

---

## This code is useful for experimentation as well

You can use this scoring system to find their engagement levels and identify targeted groups where you run experiments. For example, you have 100 users and you run the experiment on 50 and have a control group of 50. The scoring system helps you stratify users by intent level so your experiments have balanced groups and meaningful results.

---

## XGBoost

I also included optional XGBoost training files (`train_xgb.py` and `score_model.py`) to show how you can evolve from rule-based scoring to machine learning using the exact same features. The same feature pipeline works for both approaches without any modifications.

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