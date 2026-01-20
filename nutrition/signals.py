from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction, models
from .models import MealEntry, DailySummary

@receiver(post_save, sender=MealEntry)
def update_daily_summary(sender, instance, created, **kwargs):
    if instance.user.role != 'client':  
        return
    with transaction.atomic():  
        summary, _ = DailySummary.objects.get_or_create(
            user=instance.user, date=instance.date_eaten
        )
        # Aggregate all entries for the day
        entries = instance.user.meal_entries.filter(date_eaten=instance.date_eaten)
        summary.total_calories = entries.aggregate(total=models.Sum('total_calories'))['total'] or 0.0
        summary.total_protein = entries.aggregate(total=models.Sum('protein_grams'))['total'] or 0.0
        summary.total_carbs = entries.aggregate(total=models.Sum('carbs_grams'))['total'] or 0.0
        summary.total_fat = entries.aggregate(total=models.Sum('fat_grams'))['total'] or 0.0
        
        summary.save()