"""
Model Scoring Module (Optional)

Score users using a trained XGBoost model instead of rules.
Shows how the same feature pipeline works with learned models.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional


def score_with_model(
    user_df: pd.DataFrame,
    model_path: str,
    score_column: str = "model_score"
) -> pd.DataFrame:
    """
    Score users using a trained XGBoost model.
    
    Args:
        user_df: DataFrame with user features (from featurize.py)
        model_path: Path to saved XGBoost model
        score_column: Name for output score column
        
    Returns:
        DataFrame with added model_score column (probability of conversion)
    """
    try:
        import xgboost as xgb
    except ImportError:
        print("Error: xgboost not installed")
        print("Install with: pip install xgboost")
        return user_df
    
    # Load model
    try:
        model = xgb.Booster()
        model.load_model(model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        return user_df
    
    # Prepare features
    drop_cols = [
        "user_id", "username", "location_city", "gender", "primary_device",
        "last_event_ts", "converted",
        # Drop scoring columns if they exist
        "score", "score_label", "explanation", "feature_contributions", "model_score"
    ]
    
    feature_cols = [c for c in user_df.columns if c not in drop_cols]
    X = user_df[feature_cols].fillna(0)
    
    # Score
    dmatrix = xgb.DMatrix(X)
    predictions = model.predict(dmatrix)
    
    # Add to dataframe
    result_df = user_df.copy()
    result_df[score_column] = predictions
    
    return result_df


def compare_scores(
    user_df: pd.DataFrame,
    rule_score_col: str = "score",
    model_score_col: str = "model_score"
) -> None:
    """
    Print comparison between rule-based and model-based scores.
    
    Args:
        user_df: DataFrame with both rule and model scores
        rule_score_col: Column name for rule-based score
        model_score_col: Column name for model score
    """
    if rule_score_col not in user_df.columns or model_score_col not in user_df.columns:
        print("Error: Both score columns must be present")
        return
    
    # Normalize model scores to 0-100 scale
    model_scores_scaled = user_df[model_score_col] * 100
    rule_scores = user_df[rule_score_col]
    
    print("\n" + "="*70)
    print("RULE-BASED vs MODEL-BASED SCORING COMPARISON")
    print("="*70)
    
    print(f"\nRule-Based Scores:")
    print(f"  Mean:   {rule_scores.mean():.2f}")
    print(f"  Median: {rule_scores.median():.2f}")
    print(f"  Std:    {rule_scores.std():.2f}")
    
    print(f"\nModel Scores (scaled to 0-100):")
    print(f"  Mean:   {model_scores_scaled.mean():.2f}")
    print(f"  Median: {model_scores_scaled.median():.2f}")
    print(f"  Std:    {model_scores_scaled.std():.2f}")
    
    # Correlation
    corr = rule_scores.corr(model_scores_scaled)
    print(f"\nCorrelation between rule and model scores: {corr:.3f}")
    
    # Agreement on high-value users
    rule_top_20 = set(user_df.nlargest(20, rule_score_col)["user_id"])
    model_top_20 = set(user_df.nlargest(20, model_score_col)["user_id"])
    overlap = len(rule_top_20 & model_top_20)
    print(f"\nTop 20 overlap: {overlap}/20 ({100*overlap/20:.0f}%)")
    
    # Show some examples where they disagree
    user_df["score_diff"] = abs(rule_scores - model_scores_scaled)
    disagreements = user_df.nlargest(5, "score_diff")
    
    print(f"\nTop 5 Disagreements:")
    for idx, (_, r) in enumerate(disagreements.iterrows(), 1):
        print(f"\n  {idx}. {r['username']} (ID: {r['user_id']})")
        print(f"     Rule score:  {r[rule_score_col]:.1f}")
        print(f"     Model score: {r[model_score_col]*100:.1f}")
        print(f"     Difference:  {r['score_diff']:.1f}")
        if "explanation" in r.index:
            print(f"     Rule explanation: {r['explanation']}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Score users with trained XGBoost model")
    parser.add_argument(
        "--features",
        default="data/user_features.csv",
        help="Path to user features CSV"
    )
    parser.add_argument(
        "--model",
        default="models/xgb_model.json",
        help="Path to trained XGBoost model"
    )
    parser.add_argument(
        "--output",
        default="data/user_model_scores.csv",
        help="Path to save scored users"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare with rule-based scores if available"
    )
    
    args = parser.parse_args()
    
    if not Path(args.features).exists():
        print(f"Error: {args.features} not found")
        print("Run featurize.py first")
        sys.exit(1)
    
    if not Path(args.model).exists():
        print(f"Error: {args.model} not found")
        print("Run train_xgb.py first to train a model")
        sys.exit(1)
    
    print(f"Loading features from {args.features}...")
    user_df = pd.read_csv(args.features)
    
    print(f"Scoring {len(user_df)} users with XGBoost model...")
    scored_df = score_with_model(user_df, args.model)
    
    # Save
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    scored_df.to_csv(args.output, index=False)
    print(f"Scored users saved to {args.output}")
    
    # Stats
    print(f"\nModel Score Distribution:")
    scores = scored_df["model_score"]
    print(f"  Mean:   {scores.mean():.3f}")
    print(f"  Median: {scores.median():.3f}")
    print(f"  Range:  {scores.min():.3f} - {scores.max():.3f}")
    
    # Compare if requested
    if args.compare and "score" in scored_df.columns:
        compare_scores(scored_df)
