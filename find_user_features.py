import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

# Input/output paths
INPUT_PATH = Path("data/raw_events.csv")
SAMPLE_PATH = Path("data/sample-user-events.csv")
OUT_PATH = Path("data/user_features.csv")

# Helper to pick a mode value safely
def _mode_or_first(s: Any):
    m = s.mode()
    if not m.empty:
        return m.iloc[0]
    if len(s) > 0:
        return s.iloc[0]
    return None

EVENT_COLS = [
    "page_view",
    "pricing_page_view",
    "search",
    "chat_message",
    "doc_download",
    "demo_request_click",
    "signup",
    "calendar_booking",
]

def main() -> None:
    # Resolve input file (prefer a raw file, fall back to sample)
    if INPUT_PATH.exists():
        input_path = INPUT_PATH
    elif SAMPLE_PATH.exists():
        input_path = SAMPLE_PATH
        print(f"Using sample data at {input_path}")
    else:
        raise FileNotFoundError(f"Raw events file not found. Looked for {INPUT_PATH} or {SAMPLE_PATH}")

    df = pd.read_csv(input_path)

    # Parse timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)

    # Basic sanity fills
    df["scroll_depth_pct"] = pd.to_numeric(df["scroll_depth_pct"], errors="coerce")
    df["time_on_page_sec"] = pd.to_numeric(df["time_on_page_sec"], errors="coerce").fillna(0)

    # ---------- Session-level table ----------
    # One row per user_id + session_id so bounce/spam aren't double-counted across events
    session_df = (
        df.groupby(["user_id", "session_id"], as_index=False)
        .agg(
            username=("username", "first"),
            location_city=("location_city", "first"),
            gender=("gender", "first"),
            account_balance_usd=("account_balance_usd", "first"),
            recent_pages_viewed=("recent_pages_viewed", "first"),
            recent_pricing_views=("recent_pricing_views", "first"),
            is_repeat_session=("is_repeat_session", "max"),
            session_number=("session_number", "max"),
            bounce_flag=("bounce_flag", "max"),
            spam_flag=("spam_flag", "max"),
            primary_device=("device", _mode_or_first),
            session_events=("event_id", "count"),
            session_last_ts=("timestamp", "max"),
        )
    )

    # ---------- Event counts per user ----------
    # Create one-hot counts for each event type
    for ev in EVENT_COLS:
        df[ev] = (df["event_type"] == ev).astype(int)

    event_counts = (
        df.groupby("user_id", as_index=False)[EVENT_COLS]
        .sum()
        .rename(columns={
            "page_view": "page_views",
            "pricing_page_view": "pricing_page_views",
            "search": "search_events",
            "chat_message": "chat_messages",
            "doc_download": "doc_downloads",
            "demo_request_click": "demo_request_clicks",
            "signup": "signups",
            "calendar_booking": "calendar_bookings",
        })
    )

    # ---------- User-level aggregates ----------
    user_base = (
        session_df.groupby("user_id", as_index=False)
        .agg(
            username=("username", "first"),
            location_city=("location_city", "first"),
            gender=("gender", "first"),
            primary_device=("primary_device", _mode_or_first),
            account_balance_usd=("account_balance_usd", "first"),
            recent_pages_viewed=("recent_pages_viewed", "first"),
            recent_pricing_views=("recent_pricing_views", "first"),

            total_sessions=("session_id", "nunique"),
            repeat_sessions=("is_repeat_session", "sum"),
            bounces=("bounce_flag", "sum"),
            spam_sessions=("spam_flag", "sum"),

            last_event_ts=("session_last_ts", "max"),
        )
    )

    # Merge in event totals (from event table)
    user = user_base.merge(event_counts, on="user_id", how="left")

    # Total events
    total_events = df.groupby("user_id")["event_id"].count().reset_index(name="total_events")
    user = user.merge(total_events, on="user_id", how="left")

    # Rates
    user["repeat_session_rate"] = (user["repeat_sessions"] / user["total_sessions"]).fillna(0)
    user["bounce_rate"] = (user["bounces"] / user["total_sessions"]).fillna(0)
    user["spam_rate"] = (user["spam_sessions"] / user["total_sessions"]).fillna(0)

    # Ensure last_event_ts is a timestamp
    user["last_event_ts"] = pd.to_datetime(user["last_event_ts"], utc=True, errors="coerce")

    # Recency
    now = datetime.now(timezone.utc)
    user["days_since_last_event"] = (now - user["last_event_ts"]).dt.total_seconds() / (3600 * 24)

    # Label
    user["converted"] = ((user["signups"] > 0) & (user["calendar_bookings"] > 0)).astype(int)

    # ----------------- Scoring / Ranking Slice -----------------
    # Build a simple explainable score using weighted, normalized features
    import json
    import math

    # Define weights (sum to 1.0)
    weights = {
        "signups": 0.30,
        "calendar_bookings": 0.30,
        "demo_request_clicks": 0.15,
        "pricing_page_views": 0.08,
        "page_views": 0.05,
        "repeat_session_rate": 0.05,
        "account_balance_usd": 0.05,
        "recent_pages_viewed": 0.02,
    }

    # Ensure all reference columns exist
    for col in ["recent_pages_viewed", "page_views", "pricing_page_views", "demo_request_clicks", "signups", "calendar_bookings", "repeat_session_rate", "account_balance_usd"]:
        if col not in user.columns:
            user[col] = 0

    # Compute maxima for normalization (use robust measures)
    max_vals = {
        "page_views": max(1, user["page_views"].max()),
        "pricing_page_views": max(1, user["pricing_page_views"].max()),
        "demo_request_clicks": max(1, user["demo_request_clicks"].max()),
        "recent_pages_viewed": max(1, pd.to_numeric(user["recent_pages_viewed"], errors="coerce").fillna(0).max()),
        "account_balance_usd": max(1.0, user["account_balance_usd"].fillna(0).max()),
    }

    def _normalize_count(val, max_val):
        try:
            return float(val) / float(max_val) if max_val and float(max_val) > 0 else 0.0
        except Exception:
            return 0.0

    def _log_normalize(val, max_val):
        # log1p scaling for monetary amounts
        try:
            return math.log1p(float(val)) / math.log1p(float(max_val)) if max_val and float(max_val) > 0 else 0.0
        except Exception:
            return 0.0

    def score_row(r):
        # normalized feature values
        feats = {}
        feats["signups"] = 1.0 if r.get("signups", 0) > 0 else 0.0
        feats["calendar_bookings"] = 1.0 if r.get("calendar_bookings", 0) > 0 else 0.0
        feats["demo_request_clicks"] = _normalize_count(r.get("demo_request_clicks", 0), max_vals["demo_request_clicks"]) if "demo_request_clicks" in max_vals else 0.0
        feats["pricing_page_views"] = _normalize_count(r.get("pricing_page_views", 0), max_vals["pricing_page_views"]) if "pricing_page_views" in max_vals else 0.0
        feats["page_views"] = _normalize_count(r.get("page_views", 0), max_vals["page_views"]) if "page_views" in max_vals else 0.0
        feats["repeat_session_rate"] = float(r.get("repeat_session_rate", 0.0)) if pd.notnull(r.get("repeat_session_rate", 0.0)) else 0.0
        feats["account_balance_usd"] = _log_normalize(r.get("account_balance_usd", 0.0), max_vals["account_balance_usd"]) if "account_balance_usd" in max_vals else 0.0
        feats["recent_pages_viewed"] = _normalize_count(r.get("recent_pages_viewed", 0), max_vals["recent_pages_viewed"]) if "recent_pages_viewed" in max_vals else 0.0

        # recency bonus (recent activity within 30 days)
        recency = 0.0
        days = r.get("days_since_last_event")
        try:
            days = float(days)
            if days <= 30:
                recency = max(0.0, (30.0 - days) / 30.0)  # 0..1
        except Exception:
            recency = 0.0

        # incorporate recency minor weight as part of others by boosting repeat_session_rate
        feats["repeat_session_rate"] = min(1.0, feats["repeat_session_rate"] + 0.25 * recency)

        # compute raw score
        raw = 0.0
        contribs = {}
        for f, w in weights.items():
            v = feats.get(f, 0.0)
            c = w * v
            contribs[f] = round(c * 100, 3)  # contribution in percent points
            raw += c

        # scale to 0-100
        score = round(raw * 100, 2)

        # label
        if score >= 70:
            label = "high"
        elif score >= 40:
            label = "medium"
        else:
            label = "low"

        # explanation: pick top 3 contributors
        top = sorted(contribs.items(), key=lambda x: x[1], reverse=True)
        top3 = [f"{k} (+{v:.1f} pts)" for k, v in top[:3] if v > 0]
        explanation = " + ".join(top3) if top3 else "No strong signals"

        return pd.Series({
            "score": score,
            "score_label": label,
            "explanation": explanation,
            "feature_contributions": json.dumps(contribs),
        })

    score_df = user.apply(score_row, axis=1)

    user = pd.concat([user, score_df], axis=1)

    # Order columns nicely (only include columns that actually exist)
    col_order = [
        "user_id","username","location_city","gender","primary_device",
        "account_balance_usd","recent_pages_viewed","recent_pricing_views",
        "total_events","total_sessions","repeat_sessions","repeat_session_rate",
        "bounces","bounce_rate","spam_sessions","spam_rate",
        "page_views","pricing_page_views","search_events","chat_messages","doc_downloads",
        "demo_request_clicks","signups","calendar_bookings",
        "last_event_ts","days_since_last_event","converted",
        "score","score_label","explanation","feature_contributions",
    ]
    col_order = [c for c in col_order if c in user.columns]
    user = user[col_order]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    user.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(user)} users to {OUT_PATH}")

    # --------- Print scoring/ranking summary ---------
    def print_summary(df, top_n: int = 10):
        import json
        
        print("\n" + "="*70)
        print("SCORING / RANKING SLICE — SUMMARY")
        print("="*70)
        
        print(f"\n Dataset Overview:")
        print(f"   Total users scored: {len(df)}")
        converted = int(df["converted"].sum()) if "converted" in df.columns else 0
        print(f"   Converted users: {converted} ({100*converted/len(df):.1f}%)")

        # Score distribution
        if "score" in df.columns:
            s = df["score"].dropna()
            print(f"\n Score Distribution (0-100 scale):")
            print(f"   Mean:   {s.mean():6.2f}")
            print(f"   Median: {s.median():6.2f}")
            print(f"   Range:  {s.min():.2f} - {s.max():.2f}")
            print(f"   Std:    {s.std():6.2f}")

            # Label counts
            if "score_label" in df.columns:
                vc = df["score_label"].value_counts()
                total = len(df)
                print(f"\n  Score Labels:")
                for lbl in ["high", "medium", "low"]:
                    count = int(vc.get(lbl, 0))
                    pct = 100 * count / total if total > 0 else 0
                    print(f"   {lbl.capitalize():8s}: {count:3d} users ({pct:5.1f}%)")

            # Top N users with explanations
            print(f"\n Top {top_n} High-Intent Users (Ranked by Score):")
            print("-" * 70)
            top = df.sort_values("score", ascending=False).head(top_n)
            for idx, (_, r) in enumerate(top.iterrows(), 1):
                user_id = r.get('user_id', '-')
                username = r.get('username', '-')
                score = r.get('score', 0)
                label = r.get('score_label', '-')
                explanation = r.get('explanation', 'No explanation available')
                
                print(f"\n   #{idx:2d}. {username} (ID: {user_id})")
                print(f"       Score: {score:.1f}/100 [{label.upper()}]")
                print(f"       Why:   {explanation}")

            # Feature contribution analysis
            feats = {}
            if "feature_contributions" in df.columns:
                for v in df["feature_contributions"].dropna():
                    try:
                        parsed = json.loads(v)
                        for k, val in parsed.items():
                            feats[k] = feats.get(k, 0.0) + float(val)
                    except Exception:
                        continue
                
                if feats:
                    print(f"\n Feature Impact Analysis (Total Contribution Points):")
                    print("-" * 70)
                    for k, val in sorted(feats.items(), key=lambda x: x[1], reverse=True)[:8]:
                        bar_len = int(val / max(feats.values()) * 30) if feats else 0
                        bar = "█" * bar_len
                        print(f"   {k:25s} {bar:30s} {val:6.1f} pts")
            
            print("\n" + "="*70)
            print(f"✓ Full results saved to: {OUT_PATH}")
            print("="*70 + "\n")

    print_summary(user, top_n=10)

if __name__ == "__main__":
    main()
