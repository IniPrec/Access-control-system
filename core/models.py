from django.db import models
from django.utils import timezone

class User(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    ]

    full_name = models.CharField(max_length=100)
    rfid_tag = models.CharField(max_length=50, unique=True)
    photo = models.ImageField(upload_to='photo/', blank=True, null=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='student')
    created_at = models.DateTimeField(auto_now_add =True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.full_name} ({self.rfid_tag})"
    
class AccessLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    rfid_tag = models.CharField(max_length=100)
    timestamp = models.DateTimeField(default=timezone.now)
    access_granted = models.BooleanField(default=False)
    method = models.CharField(max_length=20, default='RFID') # or Camera
    reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.full_name} - {self.timestamp} - {'Granted' if self.access_granted else 'Denied'}"
    