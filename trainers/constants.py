from datetime import time

SHIFT_HOURS = {
    "morning": [(time(5, 0), time(10, 0))],
    "evening": [(time(17, 0), time(22, 0))],
    "both": [
        (time(5, 0), time(10, 0)),
        (time(17, 0), time(22, 0)),
    ],
}
