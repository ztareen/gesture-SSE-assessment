"""
Feature Engineering Module

Transforms raw event data into user-level features for scoring/modeling.
"""

import pandas as pd
from datetime import datetime, timezone
from typing import Any


def _mode_or_first(s: Any):
    """Helper to safely pick mode value or fall back to first"""
    m = s.mode()
    if not m.empty:
        return m.iloc[0]
    if len(s) > 0:
        return s.iloc[0]
    return None


def build_user_features(raw_events_path: str) -> pd.DataFrame:
    """
    Aggregate raw events into user-level features.
    
    Args:
        raw_events_path: Path to raw_events.csv
        
    Returns:
        DataFrame with one row per user containing:
        - Demographics (username, location, gender, device)
        - Account context (balance, browsing history)
        - Session metrics (total, repeat rate, bounce rate, spam rate)
        - Event counts (page views, signups, bookings, etc.)
        - Recency (days since last activity)
        - Conversion label (1 if signup + booking, else 0)
    """
    df = pd.read_csv(raw_events_path)
    
    # Parse timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    
    # Basic sanity fills
    df["scroll_depth_pct"] = pd.to_numeric(df["scroll_depth_pct"], errors="coerce")
    df["time_on_page_sec"] = pd.to_numeric(df["time_on_page_sec"], errors="coerce").fillna(0)
    
    # ---------- Session-level aggregation ----------
    # Prevents double-counting bounces/spam across multiple events in same session
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
    event_cols = [
        "page_view",
        "pricing_page_view",
        "search",
        "chat_message",
        "doc_download",
        "demo_request_click",
        "signup",
        "calendar_booking",
    ]
    
    for ev in event_cols:
        df[ev] = (df["event_type"] == ev).astype(int)
    
    event_counts = (
        df.groupby("user_id", as_index=False)[event_cols]
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
    
    # ---------- User-level aggregation ----------
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
    
    # Merge event counts
    user = user_base.merge(event_counts, on="user_id", how="left")
    
    # Total events
    total_events = df.groupby("user_id")["event_id"].count().reset_index(name="total_events")
    user = user.merge(total_events, on="user_id", how="left")
    
    # Compute rates
    user["repeat_session_rate"] = (user["repeat_sessions"] / user["total_sessions"]).fillna(0)
    user["bounce_rate"] = (user["bounces"] / user["total_sessions"]).fillna(0)
    user["spam_rate"] = (user["spam_sessions"] / user["total_sessions"]).fillna(0)
    
    # Recency
    user["last_event_ts"] = pd.to_datetime(user["last_event_ts"], utc=True, errors="coerce")
    now = datetime.now(timezone.utc)
    user["days_since_last_event"] = (now - user["last_event_ts"]).dt.total_seconds() / (3600 * 24)
    
    # Conversion label (1 if both signup and booking completed)
    user["converted"] = ((user["signups"] > 0) & (user["calendar_bookings"] > 0)).astype(int)
    
    return user


def write_user_features(user_df: pd.DataFrame, output_path: str) -> None:
    """
    Write user features to CSV with consistent column ordering.
    
    Args:
        user_df: DataFrame from build_user_features()
        output_path: Path to save CSV
    """
    # Preferred column order (only include what exists)
    col_order = [
        "user_id", "username", "location_city", "gender", "primary_device",
        "account_balance_usd", "recent_pages_viewed", "recent_pricing_views",
        "total_events", "total_sessions", "repeat_sessions", "repeat_session_rate",
        "bounces", "bounce_rate", "spam_sessions", "spam_rate",
        "page_views", "pricing_page_views", "search_events", "chat_messages", 
        "doc_downloads", "demo_request_clicks", "signups", "calendar_bookings",
        "last_event_ts", "days_since_last_event", "converted",
    ]
    
    # Only include columns that exist
    col_order = [c for c in col_order if c in user_df.columns]
    
    # Add any remaining columns not in our preferred order
    remaining = [c for c in user_df.columns if c not in col_order]
    final_cols = col_order + remaining
    
    user_df[final_cols].to_csv(output_path, index=False)
    print(f"Wrote {len(user_df)} users to {output_path}")


if __name__ == "__main__":
    # Standalone test
    import sys
    from pathlib import Path
    
    input_path = sys.argv[1] if len(sys.argv) > 1 else "data/raw_events.csv"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "data/user_features.csv"
    
    if not Path(input_path).exists():
        print(f"Error: {input_path} not found")
        sys.exit(1)
    
    print(f"Building features from {input_path}...")
    user_df = build_user_features(input_path)
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    write_user_features(user_df, output_path)
    
    print(f"\nFeature Summary:")
    print(f"  Users: {len(user_df)}")
    print(f"  Features: {len(user_df.columns)}")
    print(f"  Converted: {user_df['converted'].sum()}")
