"""
Explanation Module

Provides global and local explanations for both rule-based and model-based scoring.
"""

import pandas as pd
import json
from typing import Optional, Dict, List, Tuple


def explain_rules_global(scored_df: pd.DataFrame, top_n: int = 10) -> None:
    """
    Print global feature importance for rule-based scoring.
    
    Shows:
    - Score distribution statistics
    - Label breakdown
    - Top users by score with explanations
    - Aggregate feature contributions
    """
    print("\n" + "="*70)
    print("RULE-BASED SCORING — GLOBAL EXPLANATION")
    print("="*70)
    
    print(f"\n📊 Dataset Overview:")
    print(f"   Total users: {len(scored_df)}")
    if "converted" in scored_df.columns:
        converted = int(scored_df["converted"].sum())
        print(f"   Converted: {converted} ({100*converted/len(scored_df):.1f}%)")
    
    # Score distribution
    if "score" in scored_df.columns:
        s = scored_df["score"].dropna()
        print(f"\n📈 Score Distribution:")
        print(f"   Mean:   {s.mean():6.2f}")
        print(f"   Median: {s.median():6.2f}")
        print(f"   Range:  {s.min():.2f} - {s.max():.2f}")
        print(f"   Std:    {s.std():6.2f}")
    
    # Label counts
    if "score_label" in scored_df.columns:
        vc = scored_df["score_label"].value_counts()
        total = len(scored_df)
        print(f"\n🏷️  Score Labels:")
        for lbl in ["high", "medium", "low"]:
            count = int(vc.get(lbl, 0))
            pct = 100 * count / total if total > 0 else 0
            print(f"   {lbl.capitalize():8s}: {count:3d} users ({pct:5.1f}%)")
    
    # Top users
    if "score" in scored_df.columns and "explanation" in scored_df.columns:
        print(f"\n🎯 Top {top_n} Users by Score:")
        print("-" * 70)
        top = scored_df.sort_values("score", ascending=False).head(top_n)
        for idx, (_, r) in enumerate(top.iterrows(), 1):
            user_id = r.get('user_id', '-')
            username = r.get('username', '-')
            score = r.get('score', 0)
            label = r.get('score_label', '-')
            explanation = r.get('explanation', 'No explanation')
            
            print(f"\n   #{idx:2d}. {username} (ID: {user_id})")
            print(f"       Score: {score:.1f}/100 [{label.upper()}]")
            print(f"       Why:   {explanation}")
    
    # Aggregate feature contributions
    if "feature_contributions" in scored_df.columns:
        feats = {}
        for v in scored_df["feature_contributions"].dropna():
            try:
                parsed = json.loads(v)
                for k, val in parsed.items():
                    feats[k] = feats.get(k, 0.0) + float(val)
            except Exception:
                continue
        
        if feats:
            print(f"\n🔍 Feature Impact (Total Contribution Points):")
            print("-" * 70)
            max_contrib = max(feats.values())
            for k, val in sorted(feats.items(), key=lambda x: x[1], reverse=True)[:10]:
                bar_len = int(val / max_contrib * 30) if max_contrib > 0 else 0
                bar = "█" * bar_len
                print(f"   {k:25s} {bar:30s} {val:7.1f} pts")
    
    print("\n" + "="*70 + "\n")


def explain_rules_local(scored_df: pd.DataFrame, user_id: str) -> None:
    """
    Print detailed explanation for a specific user's score.
    """
    user_row = scored_df[scored_df["user_id"] == user_id]
    
    if len(user_row) == 0:
        print(f"Error: User {user_id} not found")
        return
    
    r = user_row.iloc[0]
    
    print("\n" + "="*70)
    print(f"LOCAL EXPLANATION — User {user_id}")
    print("="*70)
    
    print(f"\n👤 User: {r.get('username', 'N/A')}")
    print(f"   Location: {r.get('location_city', 'N/A')}")
    print(f"   Device: {r.get('primary_device', 'N/A')}")
    
    print(f"\n🎯 Score: {r.get('score', 0):.1f}/100 [{r.get('score_label', 'N/A').upper()}]")
    print(f"   {r.get('explanation', 'No explanation')}")
    
    # Feature breakdown
    if "feature_contributions" in r.index:
        try:
            contribs = json.loads(r["feature_contributions"])
            print(f"\n📊 Feature Contributions:")
            for feat, pts in sorted(contribs.items(), key=lambda x: x[1], reverse=True):
                if pts > 0:
                    bar_len = int(pts / max(contribs.values()) * 20)
                    bar = "█" * bar_len
                    print(f"   {feat:25s} {bar:20s} +{pts:5.1f} pts")
        except Exception:
            pass
    
    # Raw feature values
    print(f"\n📋 Key Features:")
    key_features = [
        "signups", "calendar_bookings", "demo_request_clicks",
        "pricing_page_views", "page_views", "repeat_session_rate",
        "account_balance_usd", "converted"
    ]
    for feat in key_features:
        if feat in r.index:
            val = r[feat]
            if pd.notnull(val):
                if isinstance(val, float):
                    print(f"   {feat:25s}: {val:.2f}")
                else:
                    print(f"   {feat:25s}: {val}")
    
    print("\n" + "="*70 + "\n")


def explain_model_global(model_path: str, feature_names: Optional[List[str]] = None) -> None:
    """
    Print global feature importance for XGBoost model.
    
    Args:
        model_path: Path to saved XGBoost model
        feature_names: Optional list of feature names (if not in model)
    """
    try:
        import xgboost as xgb
    except ImportError:
        print("Error: xgboost not installed. Run: pip install xgboost")
        return
    
    print("\n" + "="*70)
    print("XGBOOST MODEL — GLOBAL FEATURE IMPORTANCE")
    print("="*70)
    
    # Load model
    try:
        model = xgb.Booster()
        model.load_model(model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        return
    
    # Get feature importance
    importance = model.get_score(importance_type='weight')
    
    if not importance:
        print("No feature importance available")
        return
    
    print(f"\n🔍 Feature Importance (by weight):")
    print("-" * 70)
    
    sorted_feats = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    max_weight = max(importance.values())
    
    for feat, weight in sorted_feats[:15]:
        bar_len = int(weight / max_weight * 30) if max_weight > 0 else 0
        bar = "█" * bar_len
        print(f"   {feat:25s} {bar:30s} {weight:6.0f}")
    
    print("\n" + "="*70 + "\n")


def explain_model_local(
    model_path: str, 
    user_features: pd.DataFrame,
    user_id: str
) -> None:
    """
    Print local SHAP explanation for a specific user.
    
    Args:
        model_path: Path to saved XGBoost model
        user_features: DataFrame with user features
        user_id: User to explain
    """
    try:
        import xgboost as xgb
        import shap
    except ImportError:
        print("Error: xgboost and shap required. Run: pip install xgboost shap")
        return
    
    # Find user
    user_row = user_features[user_features["user_id"] == user_id]
    if len(user_row) == 0:
        print(f"Error: User {user_id} not found")
        return
    
    print("\n" + "="*70)
    print(f"SHAP EXPLANATION — User {user_id}")
    print("="*70)
    
    # Load model
    try:
        model = xgb.Booster()
        model.load_model(model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        return
    
    # Prepare features (drop non-feature columns)
    drop_cols = ["user_id", "username", "location_city", "gender", 
                 "primary_device", "last_event_ts", "converted"]
    feature_cols = [c for c in user_features.columns if c not in drop_cols]
    X_user = user_row[feature_cols]
    
    # Compute SHAP values
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_user)
    
    # Get prediction
    dmatrix = xgb.DMatrix(X_user)
    prediction = model.predict(dmatrix)[0]
    
    print(f"\n🎯 Model Prediction: {prediction:.3f}")
    print(f"   Base value: {explainer.expected_value:.3f}")
    
    # Show top SHAP contributors
    print(f"\n📊 Top SHAP Contributions:")
    shap_dict = dict(zip(feature_cols, shap_values[0]))
    sorted_shap = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)
    
    for feat, val in sorted_shap[:10]:
        direction = "↑" if val > 0 else "↓"
        print(f"   {feat:25s} {direction} {val:+.4f}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    # Standalone test
    import sys
    from pathlib import Path
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python explain.py <scored_users.csv>                    # Global rules explanation")
        print("  python explain.py <scored_users.csv> <user_id>         # Local rules explanation")
        print("  python explain.py --model <model.json>                  # Global model explanation")
        print("  python explain.py --model <model.json> <features.csv> <user_id>  # Local model explanation")
        sys.exit(1)
    
    if sys.argv[1] == "--model":
        if len(sys.argv) >= 3:
            explain_model_global(sys.argv[2])
        if len(sys.argv) >= 5:
            features = pd.read_csv(sys.argv[3])
            explain_model_local(sys.argv[2], features, sys.argv[4])
    else:
        scored_df = pd.read_csv(sys.argv[1])
        if len(sys.argv) >= 3:
            explain_rules_local(scored_df, sys.argv[2])
        else:
            explain_rules_global(scored_df)
