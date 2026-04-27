
def calculate_calories(videos, user_weight_kg):
    total_seconds = 0
    weighted_met_sum = 0.0

    for v in videos:
        total_seconds += v["effective_seconds"]
        weighted_met_sum += v["met"] * v["effective_seconds"]

    if total_seconds == 0:
        return 0, 0

    avg_met = weighted_met_sum / total_seconds
    hours = total_seconds / 3600

    calories = round(avg_met * float(user_weight_kg) * hours)  
    return total_seconds, calories