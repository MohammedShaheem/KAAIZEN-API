from google import genai
from django.conf import settings
import json
import logging
from datetime import date
import re
from ai_plan.models import WorkoutDietPlan

logger = logging.getLogger(__name__)
class AIPlanService:

    @staticmethod
    def calculate_age(dob):
        if not dob:
            return None
        today = date.today()
        return today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )

    @staticmethod
    def generate_plan(client_profile):
        # creating a gemini api client object, for preparing the connection
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        models = client.models.list()
        for m in models:
            print(m.name)
        
        age = AIPlanService.calculate_age(client_profile.date_of_birth)

        prompt = f"""
        You are a certified fitness trainer and nutritionist.

        Return STRICT JSON:

        {{
          "workout_plan": {{
            "monday": [],
            "tuesday": [],
            "wednesday": [],
            "thursday": [],
            "friday": [],
            "saturday": [],
            "sunday": []
          }},
          "diet_plan": {{
            "breakfast": "",
            "lunch": "",
            "dinner": "",
            "snacks": ""
          }},
          "estimated_calories": ""
        }}

        Client:
        Age: {age}
        Gender: {client_profile.gender}
        Height: {client_profile.height_cm}
        Weight: {client_profile.weight_kg}
        Goal: {client_profile.fitness_goal}
        """
        
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt
        )

        raw_text = response.text.strip()
        
        raw_text = re.sub(r"```json|```", "", raw_text).strip()


        logger.info(f"response from modal {response.text}")
        
           
        try:
            parsed_json = json.loads(raw_text)
            return parsed_json
        except Exception as e:
            raise ValueError("Invalid JSON from Gemini")

    @staticmethod
    def create_or_update_plan(client_profile):
        try:
            plan_data = AIPlanService.generate_plan(client_profile)
            

            plan, created = WorkoutDietPlan.objects.update_or_create(
                client=client_profile,
                defaults={"plan_data": plan_data}
            )

            return plan

        except Exception as e:
            raise