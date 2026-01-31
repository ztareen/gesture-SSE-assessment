"""
XGBoost Training Module (Optional)

Demonstrates how the same feature pipeline can support a learned model.
This is optional and shows the evolution path from rules to ML.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
import json


def prepare_training_data(
    user_features_path: str,
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Prepare features for XGBoost training.
    
    Args:
        user_features_path: Path to user_features.csv
        test_size: Fraction of data for test set
        random_state: Random seed for reproducibility
        
    Returns:
        X_train, X_test, y_train, y_test
    """
    df = pd.read_csv(user_features_path)
    
    # Target variable
    if "converted" not in df.columns:
        raise ValueError("Missing 'converted' column - run featurize.py first")
    
    y = df["converted"]
    
    # Drop non-feature columns
    drop_cols = [
        "user_id", "username", "location_city", "gender", "primary_device",
        "last_event_ts", "converted",
        # Drop scoring columns if they exist
        "score", "score_label", "explanation", "feature_contributions"
    ]
    
    X = df.drop(columns=[c for c in drop_cols if c in df.columns])
    
    # Fill missing values
    X = X.fillna(0)
    
    # Train/test split
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    return X_train, X_test, y_train, y_test


def train_xgboost(
    user_features_path: str,
    model_output_path: str,
    params: Optional[dict] = None,
    num_rounds: int = 100
) -> dict:
    """
    Train XGBoost model and save to disk.
    
    Args:
        user_features_path: Path to user_features.csv
        model_output_path: Where to save model
        params: XGBoost parameters (uses defaults if None)
        num_rounds: Number of boosting rounds
        
    Returns:
        Dictionary with training metrics
    """
    try:
        import xgboost as xgb
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
    except ImportError:
        print("Error: xgboost and sklearn required")
        print("Install with: pip install xgboost scikit-learn")
        return {}
    
    print("Preparing training data...")
    X_train, X_test, y_train, y_test = prepare_training_data(user_features_path)
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    print(f"Features: {X_train.shape[1]}")
    print(f"Positive rate: {y_train.mean():.2%}")
    
    # Default parameters
    if params is None:
        params = {
            "objective": "binary:logistic",
            "eval_metric": "logloss",
            "max_depth": 4,
            "learning_rate": 0.1,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "seed": 42
        }
    
    # Convert to DMatrix
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)
    
    # Train
    print("\nTraining XGBoost model...")
    evals = [(dtrain, "train"), (dtest, "test")]
    evals_result = {}
    
    model = xgb.train(
        params,
        dtrain,
        num_boost_round=num_rounds,
        evals=evals,
        evals_result=evals_result,
        early_stopping_rounds=10,
        verbose_eval=10
    )
    
    # Save model
    Path(model_output_path).parent.mkdir(parents=True, exist_ok=True)
    model.save_model(model_output_path)
    print(f"\nModel saved to {model_output_path}")
    
    # Evaluate
    print("\nEvaluating model...")
    y_pred_proba = model.predict(dtest)
    y_pred = (y_pred_proba >= 0.5).astype(int)
    
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, y_pred_proba),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "num_features": X_train.shape[1],
    }
    
    print("\nTest Set Metrics:")
    print(f"  Accuracy:  {metrics['accuracy']:.3f}")
    print(f"  Precision: {metrics['precision']:.3f}")
    print(f"  Recall:    {metrics['recall']:.3f}")
    print(f"  F1 Score:  {metrics['f1']:.3f}")
    print(f"  ROC AUC:   {metrics['roc_auc']:.3f}")
    
    # Save metrics
    metrics_path = Path(model_output_path).parent / "training_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\nMetrics saved to {metrics_path}")
    
    # Feature importance
    print("\nTop 10 Features by Importance:")
    importance = model.get_score(importance_type='weight')
    sorted_feats = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    for feat, weight in sorted_feats[:10]:
        print(f"  {feat:30s}: {weight:6.0f}")
    
    return metrics


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Train XGBoost model on user features")
    parser.add_argument(
        "--input",
        default="data/user_features.csv",
        help="Path to user features CSV"
    )
    parser.add_argument(
        "--output",
        default="models/xgb_model.json",
        help="Path to save trained model"
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=100,
        help="Number of boosting rounds"
    )
    
    args = parser.parse_args()
    
    if not Path(args.input).exists():
        print(f"Error: {args.input} not found")
        print("Run featurize.py first to generate user features")
        sys.exit(1)
    
    metrics = train_xgboost(
        user_features_path=args.input,
        model_output_path=args.output,
        num_rounds=args.rounds
    )
    
    if metrics:
        print("\n" + "="*70)
        print("Training complete!")
        print("="*70)
