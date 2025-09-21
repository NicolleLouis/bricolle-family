from django.db import models

class NotaryFeesOption(models.TextChoices):
    NO = "NO", "Absent"
    NEW_PROPERTY = "NEW_PROPERTY", "Neuf"
    OLD_PROPERTY = "OLD_PROPERTY", "Ancien"
