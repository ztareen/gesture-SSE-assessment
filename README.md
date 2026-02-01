# Gesture SSE Assessment — Scoring / Ranking Slice

## Overview

This system is designed to **observe and track user behavior**. After the data is captured, for each user, the output is a **numerical intent or qualification score** based on the captured data.

## Why Option C: Scoring / Ranking Slice

I chose Option C (Scoring / Ranking Slice) because:

1. **Explainability is Critical**: For a product like Gesture, stakeholders need to understand *why* a user received a particular score. Rule-based scoring provides transparent, interpretable results that can be easily explained to sales teams, product managers, and executives.

2. **Business Alignment**: Scoring directly maps to business outcomes—identifying high-intent users who are most likely to convert. This enables prioritization of sales outreach, marketing campaigns, and product features.

3. **Evolvability**: Unlike black-box ML models, rule-based systems allow for easy iteration. As we learn which signals matter most (through A/B tests, user feedback, or conversion data), we can directly adjust weights and thresholds in `score_rules.py` without retraining.

4. **Fast Implementation**: Rule-based scoring can be deployed quickly and provides immediate value, while still leaving room for ML enhancement (as shown with the optional XGBoost implementation).

5. **Trust & Debugging**: When scores seem off, we can trace exactly which features contributed and why. This builds trust with stakeholders and makes debugging straightforward.

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
The code has seperate functions, modules, and files so that everything kind of operates seperately and are brought together by the main files like main.py. I think that makes things way easier to debug because you can kind of edit individual peices without messing up the parameters of every single other part of your code. The logic that I developed can be found overall is shown in `score_rules.py`. In there, you can edit literally any of the coefficient and variables depending on what research times find as the priority in terms of clickthrough (i.e. if you find that retention and number of times a site is visited isn't as statistically significant as demographics, your values there can be edited to reflect that)

---

## This code is useful for experimentation as well

You can use this scoring system to find their engagement levels via experiments. My idea for this was basically that you can have like for example 100 users and run the experiment on 50 of the users and keep 50 as a control group. From there you can use the scoring system to effectivley stratify users by intent level so your experiments have balanced groups and then extrapolate some results. In layman's terms, you can run experiments on the data, edit the code to reflect your findings, and create a positive feedback loop of constantly improving your model.

---

## XGBoost

I also included optional XGBoost training files (`train_xgb.py` and `score_model.py`). These are more so just to show how you can develop the code even further to use ML pipelines and features to get even more optimal results. In essence, the same feature pipeline works for both approaches without any modifications.

---

## What Comes Next

### Immediate Next Steps

1. **Validate with Real Data**: Once real user interaction data is available, compare rule-based scores against actual conversion outcomes to validate and refine the weights.

2. **A/B Testing Framework**: Use the scoring system to stratify users for experiments. For example:
   - Test different messaging for high-intent vs. low-intent users
   - Measure conversion lift when prioritizing high-scoring users
   - Iterate on weights based on experiment results

3. **Feature Engineering**: Add more signals as they become available:
   - Email engagement metrics (opens, clicks)
   - Support ticket interactions
   - Product usage depth (features used, time spent)
   - Referral source and campaign attribution

4. **Threshold Calibration**: Adjust score thresholds (`DEFAULT_THRESHOLDS` in `score_rules.py`) based on:
   - Conversion rates by score bucket
   - Sales team capacity and prioritization needs
   - Business goals (growth vs. efficiency)

### Longer-Term Enhancements

1. **ML Hybrid Approach**: Use the rule-based scores as features in an ML model, combining interpretability with predictive power.

2. **Real-Time Scoring**: Move from batch processing to real-time scoring as users interact with the platform.

3. **Personalization**: Develop user-specific scoring models based on segment, industry, or use case.

4. **Dashboard & Monitoring**: Build production dashboards to track score distributions, feature importance trends, and model performance over time.

5. **Automated Retraining**: Set up pipelines to periodically retrain and validate models as new data arrives.

---

## Step by Step Instructions to Start and Run the Entire Project

### Installation

```bash
pip install -r requirements.txt
```

**Note for Windows users:** If you have Python 3 installed but `python3` doesn't work, use `py` instead of `python` or `python3` in the commands below. For example, use `py main.py` instead of `python main.py`.

### Run Complete Pipeline

```bash
py main.py --mode pipeline
```

My main file does the following (view the structure.md for more information):
1. Generate synthetic event data
2. Build user features
3. Score users with rule-based model
4. Generate ranked list of top users
5. Print global explanations

### Step-by-Step

```bash
# 1. Generate data
py main.py --mode generate --n-users 100

# 2. Build features
py main.py --mode featurize

# 3. Score users
py main.py --mode score-rules

# 4. Rank and export top users
py main.py --mode rank --n 20

# 5. Explain results
py main.py --mode explain
py main.py --mode explain --user-id user_042  # specific user
```

## Optional Frontend (React)

I've also included a minimal style react frontend in the `frontend/` folder, using Vite. It's a totally optional demo but I figured that it was a good step towards being able to see things without looking at the terminal or scanning through a CSV file. If I was given more than 3 hours to complete this assesment, that is what I would likely spend more time working on (as well as probably refining my rules and running experiments to adjust coefficients and weights in my calculations). In order to see it for yourself, just type this into the terminal: `cd frontend, then npm install, then npm run dev`.

---

## Output Files (for reference)

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