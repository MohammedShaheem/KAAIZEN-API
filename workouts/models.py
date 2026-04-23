from django.db import models
from core.models import UUIDModel,TimeStampedModel
from .choices import WorkoutDifficulty,StatusChoices
from users.models import User
from django.conf import settings
# Create your models here.

class MuscleGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Muscle Group'
        ordering = ['name']

    def __str__(self):
        return self.name
    
class WorkoutCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)

    category_image_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Workout Category"
        ordering = ["name"]

    def __str__(self):
        return self.name


# Representing single workout video
class Workout(UUIDModel, TimeStampedModel):  
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(WorkoutCategory, on_delete=models.CASCADE, related_name='workouts')
    difficulty = models.CharField(
        max_length=20,
        choices=WorkoutDifficulty.choices,
        default=WorkoutDifficulty.BEGINNER
    )
    duration_seconds = models.PositiveIntegerField()
    video_url = models.URLField(max_length=500)  
    # for generating thumbnail
    video_public_id = models.CharField(max_length=250)
    
    # for taking thumbnail from video 
    thumbnail_time = models.FloatField(default=2.0)
    equipment_needed = models.TextField(blank=True, null=True)  
    muscle_groups = models.ManyToManyField(MuscleGroup, related_name='workouts', blank=True)
    # met value for the calory calculation
    met_value = models.FloatField(default=0.0)

    class Meta:
        verbose_name = 'Workout'
        
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    
    # generating thumbnail from public_id returned by cloudinary
    def get_thumbnail_url(self):
        return (
            f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/video/upload/"
            f"so_{self.thumbnail_time}/w_400,h_225,c_fill/"
            f"{self.video_public_id}.jpg"
        )
        
    
class UserFavoriteWorkout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_workouts')
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='favorited_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User Favorite Workout'
        ordering = ['-saved_at']
        unique_together = ['user', 'workout']  

    def __str__(self):
        return f"{self.user.email} favorited {self.workout.title}"
    
    
# One session which can include many videos
class WorkoutSession(UUIDModel, TimeStampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="workout_sessions",
    )

    category = models.ForeignKey(
        WorkoutCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sessions",
    )

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
    )

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    #aggregated values calculated at end
    total_duration_seconds = models.PositiveIntegerField(default=0)
    total_calories_burned = models.PositiveIntegerField(default=0)

    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Workout Session"

    def __str__(self):
        return f"Session {self.id} - {self.user.email}"


# Specific video inside a session
class SessionVideo(models.Model):
    session = models.ForeignKey(
        WorkoutSession,
        on_delete=models.CASCADE,
        related_name="session_videos",
    )

    workout = models.ForeignKey(
        Workout,
        on_delete=models.CASCADE,
        related_name="session_entries",
    )

    #calculated from heartbeat
    effective_play_time_seconds = models.PositiveIntegerField(default=0)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["started_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["session", "workout"],
                name="unique_video_per_session",
            )
        ]
        verbose_name = "Session Video"

    def __str__(self):
        return f"{self.workout.title} in session {self.session.id}"