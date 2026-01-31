# Gesture SSE Assessment — Scoring / Ranking Slice

## Overview

This project implements a simplified user scoring and ranking system using synthetic interaction data.  
The goal is to **identify high-intent users**, assign each a score, and clearly explain why that score was given.

### The system is designed to be:

- **Explainable** — every score can be broken down into contributing factors
- **Evolvable** — features, weights, and logic can be adjusted without changing the overall pipeline
- **Production-inspired** — mirrors how real product analytics and lead-scoring systems are structured

---

## What I Built

At a high level, the pipeline looks like this:

> **Synthetic events** → **sessions** → **users** → **features** → **score + explanation**

---

### 🎲 Synthetic Interaction Data

`data/generate_users.py` generates realistic event-level interaction data for ~100 users, including:

- Page views, pricing views, demo requests, signups, calendar bookings
- Repeat sessions, bounces, and spammy behavior
- Lightweight user context (location, device, account balance, browsing summaries)

**Output:**
```
data/raw_events.csv
```

---

### ⚙️ Feature Engineering

`find_user_features.py` aggregates raw events into structured user-level features.

#### Session-level signals
*(used to avoid double-counting bounces and spam)*

#### User-level features

- **Funnel actions:** signups, calendar bookings, demo clicks
- **Engagement metrics:** repeat session rate, page views
- **Recency:** days since last activity
- **Account context:** balance and browsing history

A simple `converted` label is also created:
- **1** if the user completed both a signup and a calendar booking
- **0** otherwise

**Output:**
```
data/user_features.csv
```

---

### 🎯 Scoring + Explanation *(Core Slice)*

Each user is assigned:

1. A **score** from 0–100
2. A **label** (low, medium, high)
3. A **human-readable explanation** showing the top contributing signals

The score is computed using a **weighted, normalized model** where:

- High-intent actions (signups, calendar bookings) **dominate**
- Mid-funnel actions (demo requests, pricing views) **matter**
- Light engagement and context signals provide **small boosts**
- Recent activity **slightly increases priority**

> Every score is decomposable into per-feature contribution points, making the system easy to reason about and debug.

---

### 📊 Ranking Output

`rank_users.py` sorts users by score and outputs a short list of top candidates:

**Output:**
```
data/top_users.csv
```

This is the artifact a downstream system (sales, growth, or experimentation) would directly consume.

---

## Why I Chose This Approach

| **Principle** | **Rationale** |
|--------------|---------------|
| **Explainability first** | Avoids black-box scoring so it's always clear why one user ranks above another |
| **Session → user separation** | Prevents inflated metrics and mirrors real analytics pipelines |
| **Simple but realistic** | Intentionally small, but structured like a production system |
| **Easy to extend** | The same features can be reused for a learned model (e.g. XGBoost) without changing data preparation |

---

## Quick Start

```bash
# Generate synthetic data
python data/generate_users.py

# Extract user features
python find_user_features.py

# Rank users and output top candidates
python rank_users.py
```

---

<div align="center">

**Built with clarity, designed for scale**

</div>
