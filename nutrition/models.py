from django.db import models
from django.contrib.auth import get_user_model
from core.models import UUIDModel,TimeStampedModel
User = get_user_model()
from django.core.exceptions import ValidationError

# The details of food that an user had for one day
class DailySummary(UUIDModel,TimeStampedModel):  
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='daily_summaries',
        limit_choices_to={'role': 'client'}  
    )
    date = models.DateField(
        
    )
    total_calories = models.FloatField(
        default=0.0,
        
    )
    total_protein = models.FloatField(
        default=0.0,
        
    )
    total_carbs = models.FloatField(
        default=0.0,
        
    )
    total_fat = models.FloatField(
        default=0.0,
        
    )
    

    class Meta:
        unique_together = ['user', 'date']
        indexes = [models.Index(fields=['user', 'date'])]
        verbose_name_plural = "Daily Summaries"

    def __str__(self):
        return f"{self.user.username}'s Summary for {self.date}: {self.total_calories} kcal"

    def clean(self):
        # validation to enforce client role
       
        if self.user and self.user.role != 'client':  
            raise ValidationError("Only clients can have daily summaries.")
        super().clean()

class MealEntry(UUIDModel,TimeStampedModel):  
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('morning_snack', 'Morning Snack'),
        ('lunch', 'Lunch'),
        ('evening_snack', 'Evening Snack'),
        ('dinner', 'Dinner'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='meal_entries',
        limit_choices_to={'role': 'client'} 
    )
    meal_type = models.CharField(
        max_length=20,
        choices=MEAL_TYPES,
    )
    date_eaten = models.DateField(
    )
    time_eaten = models.TimeField(
    )
    food_description = models.TextField(
    )
    total_calories = models.FloatField(
        default=0.0,
    )
    protein_grams = models.FloatField(
        default=0.0,
    )
    carbs_grams = models.FloatField(
        default=0.0,
    )
    fat_grams = models.FloatField(
        default=0.0,
    )
    fiber_grams = models.FloatField(
        default=0.0,
    )
    source = models.CharField(
        max_length=20,
        default='manual',
        choices=[('manual','Manual'),('edamam','Edamam API')],
        
    )

    class Meta:
        indexes = [
            models.Index(fields=['user', 'date_eaten']),
            models.Index(fields=['user', 'date_eaten', 'meal_type']),
        ]
        verbose_name_plural = "Meal Entries"

    def __str__(self):
        return f"{self.user.username}'s {self.get_meal_type_display()} on {self.date_eaten}: {self.food_description[:50]}..."

    def clean(self):
        # validation to enforce clientrole
        from django.core.exceptions import ValidationError
        if self.user and self.user.role != 'client':  
            raise ValidationError("Only clients can log meals.")
        super().clean()
        
class DailySleep(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    sleep_date = models.DateField()
    sleep_start = models.DateTimeField()
    sleep_end = models.DateTimeField()
    
    hours_slept = models.DecimalField(max_digits=4, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "sleep_date")
        ordering = ["-sleep_date"]