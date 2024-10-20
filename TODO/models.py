from django.db import models

# Create your models here.
class Task(models.Model):
    title = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to='task_files/', null=True, blank=True)  # This will be uploaded to S3
    
    def __str__(self):
        return self.title