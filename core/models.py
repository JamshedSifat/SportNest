from django.db import models
import uuid

class BaseModel(models.Model):
    """
    Abstract base model - all other models will inherit from this
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True  # This won't create a database table
        ordering = ['-created_at']