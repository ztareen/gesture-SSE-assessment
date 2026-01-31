"""
Rule-Based Scoring Module

Assigns explainable scores to users based on weighted features.
This is the core of Option C: Scoring / Ranking Slice.
"""

import pandas as pd
import numpy as np
import json
import math
from typing import Dict, Optional, Tuple


# Default feature weights (sum to 1.0)
DEFAULT_WEIGHTS = {
    "signups": 0.30,                    # High-intent conversion action
    "calendar_bookings": 0.30,          # High-intent conversion action
    "demo_request_clicks": 0.15,        # Mid-funnel signal
    "pricing_page_views": 0.08,         # Interest in product value
    "page_views": 0.05,                 # General engagement
    "repeat_session_rate": 0.05,        # Sustained interest
    "account_balance_usd": 0.05,        # Financial capacity signal
    "recent_pages_viewed": 0.02,        # Browsing depth
}

# Default score thresholds
DEFAULT_THRESHOLDS = {
    "high": 70,      # Score >= 70 → high intent
    "medium": 40,    # Score >= 40 → medium intent
    # Score < 40 → low intent
}


def _normalize_count(val: float, max_val: float) -> float:
    """Normalize a count feature to [0, 1]"""
    try:
        return float(val) / float(max_val) if max_val and float(max_val) > 0 else 0.0
    except Exception:
        return 0.0


def _log_normalize(val: float, max_val: float) -> float:
    """Log-scale normalization for monetary amounts"""
    try:
        return math.log1p(float(val)) / math.log1p(float(max_val)) if max_val and float(max_val) > 0 else 0.0
    except Exception:
        return 0.0


def score_user_row(
    row: pd.Series,
    max_vals: Dict[str, float],
    weights: Dict[str, float],
    thresholds: Dict[str, float]
) -> Tuple[float, str, str, Dict[str, float]]:
    """
    Score a single user row.
    
    Returns:
        (score, label, explanation, feature_contributions)
    """
    # Normalize features to [0, 1]
    feats = {}
    
    # Binary features (0 or 1)
    feats["signups"] = 1.0 if row.get("signups", 0) > 0 else 0.0
    feats["calendar_bookings"] = 1.0 if row.get("calendar_bookings", 0) > 0 else 0.0
    
    # Count features (normalized by max)
    feats["demo_request_clicks"] = _normalize_count(
        row.get("demo_request_clicks", 0), 
        max_vals.get("demo_request_clicks", 1)
    )
    feats["pricing_page_views"] = _normalize_count(
        row.get("pricing_page_views", 0), 
        max_vals.get("pricing_page_views", 1)
    )
    feats["page_views"] = _normalize_count(
        row.get("page_views", 0), 
        max_vals.get("page_views", 1)
    )
    feats["recent_pages_viewed"] = _normalize_count(
        row.get("recent_pages_viewed", 0), 
        max_vals.get("recent_pages_viewed", 1)
    )
    
    # Rate features (already in [0, 1])
    feats["repeat_session_rate"] = float(row.get("repeat_session_rate", 0.0)) if pd.notnull(row.get("repeat_session_rate", 0.0)) else 0.0
    
    # Monetary features (log-normalized)
    feats["account_balance_usd"] = _log_normalize(
        row.get("account_balance_usd", 0.0), 
        max_vals.get("account_balance_usd", 1.0)
    )
    
    # Apply recency boost (recent activity within 30 days)
    recency_boost = 0.0
    days = row.get("days_since_last_event")
    try:
        days = float(days)
        if days <= 30:
            recency_boost = max(0.0, (30.0 - days) / 30.0)  # Linear decay from 1.0 to 0.0
    except Exception:
        pass
    
    # Add minor recency weight to repeat_session_rate
    feats["repeat_session_rate"] = min(1.0, feats["repeat_session_rate"] + 0.25 * recency_boost)
    
    # Compute weighted score
    contribs = {}
    raw_score = 0.0
    
    for feature, weight in weights.items():
        feat_val = feats.get(feature, 0.0)
        contribution = weight * feat_val
        contribs[feature] = round(contribution * 100, 3)  # Convert to percentage points
        raw_score += contribution
    
    # Scale to 0-100
    score = round(raw_score * 100, 2)
    
    # Assign label
    if score >= thresholds["high"]:
        label = "high"
    elif score >= thresholds["medium"]:
        label = "medium"
    else:
        label = "low"
    
    # Generate explanation (top 3 contributors)
    top_contributors = sorted(contribs.items(), key=lambda x: x[1], reverse=True)
    top3 = [f"{feat} (+{pts:.1f} pts)" for feat, pts in top_contributors[:3] if pts > 0]
    explanation = " + ".join(top3) if top3 else "No strong signals"
    
    return score, label, explanation, contribs


def score_users_rules(
    user_df: pd.DataFrame,
    weights: Optional[Dict[str, float]] = None,
    thresholds: Optional[Dict[str, float]] = None
) -> pd.DataFrame:
    """
    Score all users using rule-based weighted model.
    
    Args:
        user_df: DataFrame with user features (from featurize.py)
        weights: Optional custom feature weights (defaults to DEFAULT_WEIGHTS)
        thresholds: Optional custom score thresholds (defaults to DEFAULT_THRESHOLDS)
        
    Returns:
        DataFrame with added columns:
        - score: 0-100 score
        - score_label: "high", "medium", or "low"
        - explanation: Human-readable top contributors
        - feature_contributions: JSON string of all contributions
    """
    weights = weights or DEFAULT_WEIGHTS
    thresholds = thresholds or DEFAULT_THRESHOLDS
    
    # Ensure required features exist
    required_features = list(weights.keys())
    for feat in required_features:
        if feat not in user_df.columns:
            user_df[feat] = 0
    
    # Compute max values for normalization
    max_vals = {
        "page_views": max(1, user_df["page_views"].max()),
        "pricing_page_views": max(1, user_df["pricing_page_views"].max()),
        "demo_request_clicks": max(1, user_df["demo_request_clicks"].max()),
        "recent_pages_viewed": max(1, pd.to_numeric(user_df["recent_pages_viewed"], errors="coerce").fillna(0).max()),
        "account_balance_usd": max(1.0, user_df["account_balance_usd"].fillna(0).max()),
    }
    
    # Score each row
    results = []
    for _, row in user_df.iterrows():
        score, label, explanation, contribs = score_user_row(row, max_vals, weights, thresholds)
        results.append({
            "score": score,
            "score_label": label,
            "explanation": explanation,
            "feature_contributions": json.dumps(contribs)
        })
    
    # Add to dataframe
    result_df = user_df.copy()
    for key in ["score", "score_label", "explanation", "feature_contributions"]:
        result_df[key] = [r[key] for r in results]
    
    return result_df


if __name__ == "__main__":
    # Standalone test
    import sys
    from pathlib import Path
    
    input_path = sys.argv[1] if len(sys.argv) > 1 else "data/user_features.csv"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "data/user_scores.csv"
    
    if not Path(input_path).exists():
        print(f"Error: {input_path} not found")
        print("Run featurize.py first to generate user features")
        sys.exit(1)
    
    print(f"Loading features from {input_path}...")
    user_df = pd.read_csv(input_path)
    
    print(f"Scoring {len(user_df)} users...")
    scored_df = score_users_rules(user_df)
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    scored_df.to_csv(output_path, index=False)
    print(f"Wrote scored users to {output_path}")
    
    # Print summary
    print(f"\nScore Distribution:")
    print(f"  Mean:   {scored_df['score'].mean():.2f}")
    print(f"  Median: {scored_df['score'].median():.2f}")
    print(f"  Range:  {scored_df['score'].min():.2f} - {scored_df['score'].max():.2f}")
    
    print(f"\nScore Labels:")
    for label in ["high", "medium", "low"]:
        count = (scored_df["score_label"] == label).sum()
        pct = 100 * count / len(scored_df)
        print(f"  {label.capitalize():8s}: {count:3d} ({pct:5.1f}%)")
