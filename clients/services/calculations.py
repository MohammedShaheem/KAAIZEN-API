from datetime import date
from decimal import Decimal,InvalidOperation


def calculate_age(dob):
    try:
        if not dob:
            return None

        if not isinstance(dob,date):
            return None

        today = date.today()
        
        age = (
            today.year
            - dob.year
            - ((today.month,today.day) < (dob.month,dob.day))
        )
        
        return age if age > 0 else None
    
    except Exception:
        return None
    

def calculate_daily_calories(profile):
    try:
        required_attrs = [
            profile.weight,
            profile.height,
            profile.gender,
            profile.dob,
        ]
        
        if not all(required_attrs):
            return None
        
        try:
            weight = float(Decimal(profile.weight))
            height = float(profile(profile.height))
        except (InvalidOperation, TypeError, ValueError):
            return None
        
        if weight <= 0 or height <= 0:
            return None
        
        age = calculate_age(profile.dob)
        if not age:
            return None
        
        #### BMR calculation (Basal Metabolic Rate)
        gender = profile.gender.lower()
        
        if gender == "male":
            bmr  = (10 * weight) + (6.25*height) - (5*age) + 5
        elif gender == "female":
            bmr = (10*weight) + (6.25 * height) - (5*age) - 161
        else:
            bmr = (10*weight) + (6.25 * height) - (5*age)
            
        
        activity_multiplier = {
            "sedentary" : 1.2,
            "light" : 1.375,
            "moderate" : 1.55,
            "very_active" : 1.725,
        }.get(profile.daily_activity_level,1.2)
        
        maintance_calories = bmr * activity_multiplier
        
        goal_adjustment = {
            "weight_loss" : -500,
            "weight_gain" : 500,
            "muscle_gain" : 300,
            "maintenance" : 0,
            "endurance" : 200,
            "flexibility" : 0,
        }.get(profile.fitness_goal,0)
        
        target_calories = maintance_calories + goal_adjustment
        
        return int(round(target_calories))
    
    except Exception:
        return None
    

def calculate_water_goal(profile):
    try:
        if not profile.weight:
            return None

        try:
            weight = float(Decimal(profile.weight))
        except (InvalidOperation, TypeError, ValueError):
            return None
        
        if weight <= 0:
            return None
        
        base_water = weight * 35
        
        activity_bonus = {
            "sedentary":0,
            "light":250,
            "moderate":500,
            "very_active":750,
        }.get(profile.dailly_activity_level,0)
        
        return int(base_water + activity_bonus)
    
    except Exception:
        return None