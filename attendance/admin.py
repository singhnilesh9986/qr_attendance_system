from django.contrib import admin
from .models import Department, Subject, AttendanceSession, AttendanceRecord

admin.site.register(Department)
admin.site.register(Subject)
admin.site.register(AttendanceSession)
admin.site.register(AttendanceRecord)
