from django.db import models

class UserRole(models.TextChoices):
    ADMIN = "admin","Admin"
    TRAINER = "trainer","Trainer"
    CLIENT = "client","Client"