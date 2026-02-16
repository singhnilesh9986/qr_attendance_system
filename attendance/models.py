from django.db import models
from django.contrib.auth.models import User
import uuid

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True) 

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.department.name})"

class AttendanceSession(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    day_number = models.IntegerField() 
    session_number = models.IntegerField() 
    date = models.DateField(auto_now_add=True)
    
   
    admin_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    admin_long = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    current_token = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    radius_meters = models.IntegerField(default=200) 
    
    def refresh_token(self):
        self.current_token = str(uuid.uuid4())
        self.save()

    def __str__(self):
        return f"Day {self.day_number} - {self.subject.name}"

class AttendanceRecord(models.Model):
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
   
    student_lat = models.DecimalField(max_digits=9, decimal_places=6)
    student_long = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        unique_together = ('session', 'student') 

    def __str__(self):
        return f"{self.student.username} - {self.session}"








