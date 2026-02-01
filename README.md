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
The code has seperate functions, modules, and files so that everything kind of operates seperately and are brought together by the main files like main.py. I think that makes things way easier to debug because you can kind of edit individual peices without messing up the parameters of every single other part of your code. The logic that I developed can be found overall is shown in `score_rules.py`. In there, you can edit literally any of the coefficient and variables depending on what research times find as the priority in terms of clickthrough (i.e. if you find that retention and number of times a site is visited isn't as statistically significant as demographics, your values there can be edited to reflect that)

---

## This code is useful for experimentation as well

You can use this scoring system to find their engagement levels via experiments. My idea for this was basically that you can have like for example 100 users and run the experiment on 50 of the users and keep 50 as a control group. From there you can use the scoring system to effectivley stratify users by intent level so your experiments have balanced groups and then extrapolate some results. In layman's terms, you can run experiments on the data, edit the code to reflect your findings, and create a positive feedback loop of constantly improving your model.

---

## XGBoost

I also included optional XGBoost training files (`train_xgb.py` and `score_model.py`). These are more so just to show how you can develop the code even further to use ML pipelines and features to get even more optimal results. In essence, the same feature pipeline works for both approaches without any modifications.

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

This runs the full pipeline and will automatically start a small local web server and open a browser-based results dashboard (http://localhost:8000); the page uses results.html or the built frontend if present.

## Optional Frontend (React)

I've also included a minimal style react frontend in the `frontend/` folder, using Vite. It's a totally optional demo but I figured that it was a good step towards being able to see things without looking at the terminal or scanning through a CSV file. If I was given more than 3 hours to complete this assesment, that is what I would likely spend more time working on (as well as probably refining my rules and running experiments to adjust coefficients and weights in my calculations). In order to see it for yourself, just type this into the terminal: `cd frontend, then npm install, then npm run dev`.

---

## Next Steps

If I were given more time (say a week) to complete this project, I would likely do the following:
1. Try and do some feature engineering for finding product usage depth (features used, time spent), and also email engagement metrics like opens and clicks
2. I would try and validate how accurate my information is with real data
3. I would run linear regression to understand in a little more detail how accurate my output is
4. I would try and run some real-time scoring rather than this model which works off of existing CSVs
5. I would attempt to integrate XGBoost and more ML concepts


## Output Files Found @ the "Structure" File in this Repository!