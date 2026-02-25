from django.db import models

class UserRole(models.TextChoices):
    ADMIN = "admin","Admin"
    TRAINER = "trainer","Trainer"
    CLIENT = "client","Client"
    

class EntryType(models.TextChoices):
    CREDIT = "credit", "Credit"
    DEBIT = "debit", "Debit"

class Status(models.TextChoices):
    PENDING = "pending", "Pending"
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"