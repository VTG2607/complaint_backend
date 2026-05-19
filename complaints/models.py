from django.db import models
from django.conf import settings
# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Complaint(models.Model):

    
    class Status(models.TextChoices):
        SUBMITTED = "SUBMITTED"
        IN_PROGRESS = "IN_PROGRESS"
        RESOLVED = "RESOLVED"
        REJECTED = "REJECTED"


    class Priority(models.TextChoices):
        LOW = "LOW"
        MEDIUM = "MEDIUM"
        HIGH = "HIGH"


    title = models.CharField(max_length=200)
    body = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, max_length=100, null=True, blank=True, on_delete=models.SET_NULL)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.LOW)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)

    def __str__(self):
        return self.title


class Comments(models.Model):
    complaint = models.ForeignKey(Complaint, related_name="comments", on_delete=models.CASCADE)
    comment_body = models.TextField()
    comment_author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.comment_author} on '{self.complaint.title}'"
