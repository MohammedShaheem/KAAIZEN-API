from datetime import time

SESSION_TYPES = {
    "morning": (time(5, 0), time(10, 0)),
    "evening": (time(17, 0), time(22, 0)),
}

SESSIONS_PER_CYCLE = 6
