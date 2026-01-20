from rest_framework import serializers
from ..models import MealEntry
from django.utils import timezone
from datetime import datetime
import requests
from django.conf import settings


class MealEntrySerializer(serializers.ModelSerializer):
    # Input fields 
    print("mealentryserializerentering here")
    food_description = serializers.CharField(required=True)
    meal_type = serializers.ChoiceField(choices=MealEntry.MEAL_TYPES)
    date_eaten = serializers.DateField(required=True)
    time_eaten = serializers.TimeField(required=True)

    class Meta:
        model = MealEntry
        fields = [
            'id', 'food_description', 'meal_type', 'date_eaten', 'time_eaten',
            'total_calories', 'protein_grams', 'carbs_grams', 'fat_grams', 'fiber_grams',
            'source',  
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'total_calories', 'protein_grams', 'carbs_grams',
            'fat_grams', 'fiber_grams', 'source', 
            'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        
        user = self.context['request'].user
        if user.role != 'client':
            raise serializers.ValidationError("Only clients can log meals.")

        food_description = validated_data['food_description']
        print("FOOD DESC:", food_description)

        # Call Edamam
        nutrition_data = self.fetch_edamam_nutrition(food_description)
        print("RAW NUTRITION DATA KEYS:", list(nutrition_data.keys()) if nutrition_data else "None")  
        if not nutrition_data:
            print("EDAMAM RETURNED NONE FALLING BACK TO MANUAL")
            self._update_validated_with_zeros(validated_data)
            return MealEntry.objects.create(user=user, **validated_data)

        
        total_nutrients = nutrition_data.get('totalNutrients', {})
        total_calories = nutrition_data.get('calories', 0.0)
        print("PRIMARY TOTAL_NUTRIENTS KEYS:", list(total_nutrients.keys()) if total_nutrients else "Empty!")  

        if total_nutrients and total_calories > 0:
            print("USING AGGREGATED TOTAL_NUTRIENTS")
            validated_data.update({
                'total_calories': total_calories,
                'protein_grams': self._extract_nutrient(total_nutrients, 'PROCNT'),
                'carbs_grams': self._extract_nutrient(total_nutrients, 'CHOCDF'),
                'fat_grams': self._extract_nutrient(total_nutrients, 'FAT'),
                'fiber_grams': self._extract_nutrient(total_nutrients, 'FIBTG'),
                'source': 'edamam'  
            })
        else:
            
            print("FALLING BACK TO SUMMING PER-INGREDIENT NUTRIENTS")
            summed_nutrients = self._sum_per_ingredient_nutrients(nutrition_data)
            validated_data.update({
                'total_calories': summed_nutrients.get('calories', 0.0),
                'protein_grams': summed_nutrients.get('protein', 0.0),
                'carbs_grams': summed_nutrients.get('carbs', 0.0),
                'fat_grams': summed_nutrients.get('fat', 0.0),
                'fiber_grams': summed_nutrients.get('fiber', 0.0),
                'source': 'edamam'  
            })
            print("SUMMED VALUES - Calories:", validated_data['total_calories'], "Protein:", validated_data['protein_grams'])  

        
        meal_entry = MealEntry.objects.create(user=user, **validated_data)
        print("MEAL ENTRY CREATED:", meal_entry.id)
        return meal_entry

    def _update_validated_with_zeros(self, validated_data):
        # Fallback for no data at all
        validated_data.update({
            'total_calories': 0.0,
            'protein_grams': 0.0,
            'carbs_grams': 0.0,
            'fat_grams': 0.0,
            'fiber_grams': 0.0,
            'source': 'manual'  
        })

    def fetch_edamam_nutrition(self, ingredient):
        # Fetch from Edamam Nutrition Details API 
        url = "https://api.edamam.com/api/nutrition-details"
        params = {
            'app_id': settings.EDAMAM_APP_ID,
            'app_key': settings.EDAMAM_APP_KEY,
        }
        payload = {
            'ingr': [ingredient]  # array of strings for multi-items
        }
        try:
            response = requests.post(
                url,
                params=params,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            print("EDAMAM STATUS:", response.status_code)
            return data
        except requests.RequestException as e:
            print(f"Edamam API error: {e}")
            return None

    def _extract_nutrient(self, nutrients_dict, label):
        # Extract quantity from nutrients dict 
        nutrient = nutrients_dict.get(label, {})
        quantity = float(nutrient.get('quantity', 0.0))
        print(f"EXTRACTED {label}: {quantity}")
        return quantity

    def _sum_per_ingredient_nutrients(self, data):
        # Sum nutrients across all parsed ingredients
        summed = {
            'calories': 0.0,
            'protein': 0.0,
            'carbs': 0.0,
            'fat': 0.0,
            'fiber': 0.0
        }
        ingredients = data.get('ingredients', [])
        for ing in ingredients:
            for parsed in ing.get('parsed', []):
                nut = parsed.get('nutrients', {})
                
                summed['calories'] += nut.get('ENERC_KCAL', {}).get('quantity', 0.0)
                
                summed['protein'] += nut.get('PROCNT', {}).get('quantity', 0.0)
                
                summed['carbs'] += nut.get('CHOCDF', {}).get('quantity', 0.0)
                
                summed['fat'] += nut.get('FAT', {}).get('quantity', 0.0)
                
                summed['fiber'] += nut.get('FIBTG', {}).get('quantity', 0.0)
        print(f"SUMMED FROM INGREDIENTS: {summed}")  
        return summed