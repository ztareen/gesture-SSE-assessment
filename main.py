#!/usr/bin/env python3
"""
Main Orchestration Script

Runs the complete scoring/ranking pipeline or individual components.
"""

import argparse
import sys
from pathlib import Path
import pandas as pd


def run_generate(args):
    """Generate synthetic event data"""
    from data.generate_users import generate_users
    
    print(f"Generating {args.n_users} users...")
    output_path = Path(args.output) if args.output else Path("data/raw_events.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    generate_users(
        output_path=str(output_path),
        n_users=args.n_users,
        seed=args.seed
    )
    print(f"Generated events saved to {output_path}")


def run_featurize(args):
    """Build user features from raw events"""
    from featurize import build_user_features, write_user_features
    
    input_path = Path(args.input) if args.input else Path("data/raw_events.csv")
    output_path = Path(args.output) if args.output else Path("data/user_features.csv")
    
    if not input_path.exists():
        print(f"Error: {input_path} not found")
        print("Run with --mode generate first")
        sys.exit(1)
    
    print(f"Building features from {input_path}...")
    user_df = build_user_features(str(input_path))
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_user_features(user_df, str(output_path))
    
    print(f"\nFeature Summary:")
    print(f"  Users: {len(user_df)}")
    print(f"  Features: {len(user_df.columns)}")
    print(f"  Converted: {user_df['converted'].sum()}")


def run_score_rules(args):
    """Score users using rule-based model"""
    from score_rules import score_users_rules
    
    input_path = Path(args.input) if args.input else Path("data/user_features.csv")
    output_path = Path(args.output) if args.output else Path("data/user_scores.csv")
    
    if not input_path.exists():
        print(f"Error: {input_path} not found")
        print("Run with --mode featurize first")
        sys.exit(1)
    
    print(f"Loading features from {input_path}...")
    user_df = pd.read_csv(input_path)
    
    print(f"Scoring {len(user_df)} users with rule-based model...")
    scored_df = score_users_rules(user_df)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    scored_df.to_csv(output_path, index=False)
    print(f"Scored users saved to {output_path}")
    
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
    
    # Optionally show top users
    if args.show_top:
        print(f"\nTop {args.show_top} Users:")
        top = scored_df.sort_values("score", ascending=False).head(args.show_top)
        for idx, (_, r) in enumerate(top.iterrows(), 1):
            print(f"  {idx}. {r['username']} - {r['score']:.1f} ({r['score_label']}) - {r['explanation']}")


def run_explain(args):
    """Generate explanations for scored users"""
    from explain import explain_rules_global, explain_rules_local
    
    input_path = Path(args.input) if args.input else Path("data/user_scores.csv")
    
    if not input_path.exists():
        print(f"Error: {input_path} not found")
        print("Run with --mode score-rules first")
        sys.exit(1)
    
    scored_df = pd.read_csv(input_path)
    
    if args.user_id:
        explain_rules_local(scored_df, args.user_id)
    else:
        explain_rules_global(scored_df, top_n=args.top_n)


def run_rank(args):
    """Generate ranked list of top users"""
    input_path = Path(args.input) if args.input else Path("data/user_scores.csv")
    output_path = Path(args.output) if args.output else Path("data/top_users.csv")
    
    if not input_path.exists():
        print(f"Error: {input_path} not found")
        print("Run with --mode score-rules first")
        sys.exit(1)
    
    scored_df = pd.read_csv(input_path)
    
    # Select top N by score
    top_users = scored_df.sort_values("score", ascending=False).head(args.n)
    
    # Select relevant columns for output
    output_cols = [
        "user_id", "username", "score", "score_label", "explanation",
        "signups", "calendar_bookings", "demo_request_clicks",
        "pricing_page_views", "converted"
    ]
    output_cols = [c for c in output_cols if c in top_users.columns]
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    top_users[output_cols].to_csv(output_path, index=False)
    print(f"Top {len(top_users)} users saved to {output_path}")
    
    # Print preview
    print(f"\nTop {min(5, len(top_users))} Users:")
    for idx, (_, r) in enumerate(top_users.head(5).iterrows(), 1):
        print(f"  {idx}. {r['username']} - {r['score']:.1f} [{r['score_label'].upper()}]")
        print(f"     {r['explanation']}")


def run_pipeline(args):
    """Run the complete pipeline end-to-end"""
    print("="*70)
    print("RUNNING COMPLETE PIPELINE")
    print("="*70)
    
    # Step 1: Generate
    print("\n[1/5] Generating synthetic data...")
    class GenArgs:
        n_users = args.n_users
        seed = args.seed
        output = "data/raw_events.csv"
    run_generate(GenArgs())
    
    # Step 2: Featurize
    print("\n[2/5] Building user features...")
    class FeatArgs:
        input = "data/raw_events.csv"
        output = "data/user_features.csv"
    run_featurize(FeatArgs())
    
    # Step 3: Score
    print("\n[3/5] Scoring users...")
    class ScoreArgs:
        input = "data/user_features.csv"
        output = "data/user_scores.csv"
        show_top = 0
    run_score_rules(ScoreArgs())
    
    # Step 4: Rank
    print("\n[4/5] Generating ranked list...")
    class RankArgs:
        input = "data/user_scores.csv"
        output = "data/top_users.csv"
        n = 20
    run_rank(RankArgs())
    
    # Step 5: Explain
    print("\n[5/5] Generating explanations...")
    class ExplainArgs:
        input = "data/user_scores.csv"
        user_id = None
        top_n = 10
    run_explain(ExplainArgs())
    
    print("\n" + "="*70)
    print("PIPELINE COMPLETE")
    print("="*70)
    print("\nOutputs:")
    print("  data/raw_events.csv   - Synthetic event data")
    print("  data/user_features.csv - Engineered features")
    print("  data/user_scores.csv   - Scored users")
    print("  data/top_users.csv     - Top ranked users")


def main():
    parser = argparse.ArgumentParser(
        description="User Scoring & Ranking Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete pipeline
  py main.py --mode pipeline
  
  # Run individual steps
  py main.py --mode generate --n-users 100
  py main.py --mode featurize
  py main.py --mode score-rules
  py main.py --mode rank --n 20
  py main.py --mode explain
  
  # Explain specific user
  py main.py --mode explain --user-id user_001
  
Note: On Windows, use 'py' instead of 'python' or 'python3' if needed.
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["pipeline", "generate", "featurize", "score-rules", "rank", "explain"],
        default="pipeline",
        help="Which step to run (default: pipeline)"
    )
    
    # Generate args
    parser.add_argument("--n-users", type=int, default=100, help="Number of users to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    
    # Generic I/O args
    parser.add_argument("--input", help="Input file path")
    parser.add_argument("--output", help="Output file path")
    
    # Score args
    parser.add_argument("--show-top", type=int, default=0, help="Show top N users in scoring")
    
    # Rank args
    parser.add_argument("--n", type=int, default=20, help="Number of top users to output")
    
    # Explain args
    parser.add_argument("--user-id", help="Explain specific user")
    parser.add_argument("--top-n", type=int, default=10, help="Number of top users to show")
    
    args = parser.parse_args()
    
    # Route to appropriate function
    mode_handlers = {
        "pipeline": run_pipeline,
        "generate": run_generate,
        "featurize": run_featurize,
        "score-rules": run_score_rules,
        "rank": run_rank,
        "explain": run_explain,
    }
    
    handler = mode_handlers[args.mode]
    handler(args)


if __name__ == "__main__":
    main()
