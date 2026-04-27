from datetime import date
from decimal import Decimal,InvalidOperation
import logging

logger = logging.getLogger(__name__)


def calculate_age(dob):
    try:
        if not dob or not isinstance(dob,date):
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
    logger.info("from calculate daily calory")


    try:
        weight_raw  = profile.get("weight_kg")
        height_raw  = profile.get("height_cm")
        gender      = profile.get("gender")
        dob         = profile.get("date_of_birth")

        
        if not all([weight_raw, height_raw, gender, dob]):
            return None
        
        
        try:
            weight = float(Decimal(str(weight_raw)))
            height = float(Decimal(str(height_raw)))
        except (InvalidOperation, TypeError, ValueError):
            return None
        
        if weight <= 0 or height <= 0:
            return None
        
        age = calculate_age(dob)
        if not age:
            return None

        
        
        # BMR calculation (Basal Metabolic Rate)
        gender = gender.lower()
        if gender == "male":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        elif gender == "female":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age)
            
        
        activity_multipliers = {
            "sedentary":   1.2,
            "light":       1.375,
            "moderate":    1.55,
            "very_active": 1.725,
        }
        multiplier = activity_multipliers.get(
            profile.get("daily_activity_level"), 1.2
        )
        maintenance_calories = bmr * multiplier

        
        goal_adjustments = {
            "weight_loss": -500,
            "weight_gain":  500,
            "muscle_gain":  300,
            "maintenance":    0,
            "endurance":    200,
            "flexibility":    0,
        }
        goal_adjustment = goal_adjustments.get(profile.get("fitness_goal"), 0)

        target_calories = maintenance_calories + goal_adjustment
        logger.debug(
            f"BMR={bmr:.1f}, multiplier={multiplier}, "
            f"maintenance={maintenance_calories:.1f}, "
            f"adjustment={goal_adjustment}, target={target_calories:.1f}"
        )
        return int(round(target_calories))
    
    except Exception as e:
        logger.error("error from try of calculation",e)
        return None
    

def calculate_water_goal(profile):
    try:
        weight_raw = profile.get("weight_kg")  
        if not weight_raw:
            return None

        try:
            weight = float(Decimal(str(weight_raw)))  
        except (InvalidOperation, TypeError, ValueError):
            return None
        
        if weight <= 0:
            return None
        
        base_water = weight * 35
        
        activity_bonus = {
            "sedentary": 0,
            "light": 250,
            "moderate": 500,
            "very_active": 750,
        }.get(profile.get("daily_activity_level"), 0)
        
        return int(base_water + activity_bonus)
    
    except Exception as e:
        logger.error("calculate_water_goal error: %s", e)  
        return None
    

def calculate_daily_calorie_burn_goal(profile):
    try:
        weight_raw = profile.get("weight_kg")
        height_raw = profile.get("height_cm")
        gender     = profile.get("gender")
        dob        = profile.get("date_of_birth")

        if not all([weight_raw, height_raw, gender, dob]):
            return None

        try:
            weight = float(Decimal(str(weight_raw)))
            height = float(Decimal(str(height_raw)))
        except (InvalidOperation, TypeError, ValueError):
            return None

        age = calculate_age(dob)
        if not age:
            return None

        gender = gender.lower()
        if gender == "male":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        elif gender == "female":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age)

        activity_multipliers = {
            "sedentary":   1.2,
            "light":       1.375,
            "moderate":    1.55,
            "very_active": 1.725,
        }
        multiplier = activity_multipliers.get(
            profile.get("daily_activity_level"), 1.2
        )

        
        tdee = bmr * multiplier

        
        goal_burn_adjustments = {
            "weight_loss":  300,   
            "weight_gain": -200,   
            "muscle_gain":  100,   
            "maintenance":    0,
            "endurance":    400,   
            "flexibility":    0,
        }
        adjustment = goal_burn_adjustments.get(profile.get("fitness_goal"), 0)

        burn_goal = tdee + adjustment

        logger.debug(
            f"BMR={bmr:.1f}, TDEE={tdee:.1f}, "
            f"burn_adjustment={adjustment}, burn_goal={burn_goal:.1f}"
        )
        return int(round(burn_goal))

    except Exception as e:
        logger.error(f"calculate_daily_calorie_burn_goal error: {e}")
        return None