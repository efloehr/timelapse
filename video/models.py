from django.db import models
from image.models import Normal

# Create your models here.
class Info(models.Model):
    DAYLIGHT = 1
    NIGHT    = 2
    ALL_DAY  = 3
    KINDS = (
        (DAYLIGHT, "Standard Daylight Video"),
        (NIGHT,    "Standard Night Video"),
        (ALL_DAY,  "All Day 24h Movie"),
    )
    
    # Metadata
    day = models.DateField(db_index=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    kind = models.SmallIntegerField(choices=KINDS)
    
    # File Info
    filepath = models.CharField(max_length=1024, unique=True)
    filename = models.CharField(max_length=255, unique=True, null=True)
    size = models.BigIntegerField(default=-1)
    
    class Meta:
        ordering = ['day']
