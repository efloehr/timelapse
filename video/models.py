from django.db import models
from image.models import Normal

# Create your models here.
class Info(models.Model):
    KINDS = (
        (1, "Standard Daylight Video"),
        (2, "Standard Night Video"),
    )
    
    # Metadata
    day = models.DateField(db_index=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    kind = models.SmallIntegerField(choices=KINDS)
    
    # File Info
    filepath = models.CharField(max_length=1024, unique=True)
    filename = models.CharField(max_length=255, unique=True, null=True)
    size = models.IntegerField(default=0)
    
    # Raw images used
    images = models.ManyToManyField(Normal)
    
    class Meta:
        ordering = ['day']
        abstract = True
