import csv
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

# ---------- Config ----------
NUM_USERS = 100
MIN_SESSIONS_PER_USER = 1
MAX_SESSIONS_PER_USER = 5
MIN_EVENTS_PER_SESSION = 1
MAX_EVENTS_PER_SESSION = 8
DAYS_BACK = 30

OUTPUT_PATH = Path("data/raw_events.csv")

EVENT_TYPES = [
    "page_view",
    "pricing_page_view",
    "search",
    "chat_message",
    "doc_download",
    "demo_request_click",
    "signup",
    "calendar_booking",
]

CITIES = ["San Francisco", "New York", "Toronto", "London", "Bangalore"]
DEVICES = ["desktop", "mobile"]
GENDERS = ["male", "female", "non_binary", "undisclosed"]

# A small base pool; we’ll make them unique with suffixes.
BASE_USERNAMES = [
    "alex_chen", "sarah_k", "jordan_m", "mike_t", "priya_p",
    "daniel_r", "emma_w", "liam_h", "noah_b", "olivia_s",
    "ethan_c", "maya_g", "nina_d", "chris_j", "guest",
]


@dataclass(frozen=True)
class UserProfile:
    user_id: str
    username: str
    location_city: str
    gender: str
    account_balance_usd: float
    recent_pages_viewed: int
    recent_pricing_views: int


def rand_ts(now: datetime) -> str:
    # Random timestamp within the last DAYS_BACK days
    delta = timedelta(days=random.randint(0, DAYS_BACK), seconds=random.randint(0, 86400))
    return (now - delta).replace(microsecond=0).isoformat()


def sample_user_profile(i: int) -> UserProfile:
    user_id = f"u{i:04d}"

    # Unique username: base + short suffix
    base = random.choice(BASE_USERNAMES)
    username = f"{base}_{i:02d}"

    location_city = random.choice(CITIES)
    gender = random.choice(GENDERS)

    # Synthetic “wallet” style balance: many small, some large
    balance = max(0.0, random.gauss(200, 350))
    account_balance_usd = round(balance, 2)

    # Browsing history summary: aggregated signals, not raw URL trails
    recent_pages = random.randint(0, 15)
    recent_pricing = random.randint(0, min(5, recent_pages))

    return UserProfile(
        user_id=user_id,
        username=username,
        location_city=location_city,
        gender=gender,
        account_balance_usd=account_balance_usd,
        recent_pages_viewed=recent_pages,
        recent_pricing_views=recent_pricing,
    )


def choose_event_type(intent: float) -> str:
    # Higher intent -> more likely pricing/demo/signup/calendar
    if intent > 0.85:
        return random.choices(
            EVENT_TYPES,
            weights=[2, 4, 1, 2, 2, 3, 2, 2],
            k=1
        )[0]
    else:
        return random.choices(
            EVENT_TYPES,
            weights=[7, 1, 3, 1, 1, 0.2, 0.1, 0.05],
            k=1
        )[0]


def main() -> None:
    now = datetime.utcnow()

    rows = []
    event_counter = 1

    # Pre-create stable user profiles
    users = [sample_user_profile(i) for i in range(NUM_USERS)]

    for user in users:
        sessions = random.randint(MIN_SESSIONS_PER_USER, MAX_SESSIONS_PER_USER)

        for s in range(sessions):
            session_id = f"s{random.randint(1000, 9999)}"
            session_number = s + 1
            is_repeat_session = int(s > 0)

            n_events = random.randint(MIN_EVENTS_PER_SESSION, MAX_EVENTS_PER_SESSION)
            intent = random.random()

            bounce_flag = int(n_events == 1)

            # spam heuristic: low balance + bounce + very low intent
            spam_flag = int(bounce_flag == 1 and intent < 0.05 and user.account_balance_usd < 5)

            for _ in range(n_events):
                event_type = choose_event_type(intent)

                # Page metrics: only meaningful for page/pricing views
                if event_type in ("page_view", "pricing_page_view"):
                    time_on_page_sec = random.randint(5, 120)
                    scroll_depth_pct = random.randint(5, 100)
                else:
                    time_on_page_sec = 0
                    scroll_depth_pct = ""

                rows.append({
                    "event_id": f"e{event_counter:06d}",
                    "user_id": user.user_id,
                    "username": user.username,
                    "session_id": session_id,
                    "timestamp": rand_ts(now),
                    "event_type": event_type,
                    "location_city": user.location_city,
                    "device": random.choice(DEVICES),
                    "is_repeat_session": is_repeat_session,
                    "session_number": session_number,
                    "account_balance_usd": user.account_balance_usd,
                    "recent_pages_viewed": user.recent_pages_viewed,
                    "recent_pricing_views": user.recent_pricing_views,
                    "gender": user.gender,
                    "time_on_page_sec": time_on_page_sec,
                    "scroll_depth_pct": scroll_depth_pct,
                    "bounce_flag": bounce_flag,
                    "spam_flag": spam_flag,
                })

                event_counter += 1

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(rows[0].keys()) if rows else []
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
