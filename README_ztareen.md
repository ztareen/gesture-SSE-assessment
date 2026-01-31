Gesture SSE Assessment — Scoring / Ranking Slice
Overview

This project implements a simplified user scoring and ranking system using synthetic interaction data.
The goal is to identify high-intent users, assign each a score, and clearly explain why that score was given.

The system is designed to be:

Explainable: every score can be broken down into contributing factors

Evolvable: features, weights, and logic can be adjusted without changing the overall pipeline

Production-inspired: mirrors how real product analytics and lead-scoring systems are structured

What I Built

At a high level, the pipeline looks like this:

Synthetic events → sessions → users → features → score + explanation

1. Synthetic Interaction Data

data/generate_users.py generates realistic event-level interaction data for ~100 users, including:

Page views, pricing views, demo requests, signups, calendar bookings

Repeat sessions, bounces, and spammy behavior

Lightweight user context (location, device, account balance, browsing summaries)

This produces data/raw_events.csv.

2. Feature Engineering

find_user_features.py aggregates raw events into:

Session-level signals (to avoid double-counting bounces/spam)

User-level features, such as:

Funnel actions (signups, bookings, demo clicks)

Engagement metrics (repeat session rate, page views)

Recency (days since last activity)

Basic account context (balance, browsing history)

It also creates a simple converted label (signup + calendar booking).

The output is data/user_features.csv.

3. Scoring + Explanation (Core Slice)

Each user is assigned:

A score from 0–100

A label (low, medium, high)

A human-readable explanation showing the top contributing signals

The score is computed using a weighted, normalized model where:

High-intent actions (signups, calendar bookings) dominate

Mid-funnel actions (demo requests, pricing views) matter

Light engagement and context signals provide small boosts

Recent activity slightly increases priority

Every score is decomposable into per-feature contribution points, which makes the system easy to reason about and debug.

4. Ranking Output

rank_users.py sorts users by score and outputs a short list of the top candidates (data/top_users.csv), which is the artifact a downstream system (sales, growth, experiments) would actually consume.

Why I Chose This Approach

Explainability first: I avoided black-box scoring so it’s always clear why a user ranks above another.

Session → user separation: prevents inflated metrics and mirrors real analytics pipelines.

Simple but realistic: the system is intentionally small, but structured the way a production version would be.

Easy to extend: the same features can be fed into a learned model (e.g. XGBoost) without changing data prep.