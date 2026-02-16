from django.shortcuts import render, redirect
from django.http import JsonResponse 
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from django.contrib.auth.decorators import login_required
from .models import Department, Subject, AttendanceSession, AttendanceRecord
import json
from math import radians, cos, sin, asin, sqrt



def haversine(lat1, lon1, lat2, lon2):
    
    R = 6371000 
    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * R

@login_required
def submit_attendance(request):
    if request.method == "POST":
        data = json.loads(request.body)
        token = data.get('token')
        s_lat = data.get('student_lat')
        s_long = data.get('student_long')

        
        session = AttendanceSession.objects.filter(current_token=token, status='active').first()
        
        if not session:
            return JsonResponse({"status": "error", "message": "Invalid or expired QR code."})

      
        distance = haversine(s_lat, s_long, session.admin_lat, session.admin_long)
        adjusted_distance = max(0, distance - 10)
        if adjusted_distance <= session.radius_meters:
            
            AttendanceRecord.objects.get_or_create(
                session=session,
                student=request.user,
                defaults={'student_lat': s_lat, 'student_long': s_long}
            )
         
            session.refresh_token() 
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "error", "message": f"Too far! You are {int(distance)}m away."})
            
    return JsonResponse({"status": "error", "message": "Invalid request."})

def home(request):
    return render(request,'attendance/home.html')

def login_selection(request):
    return render(request, 'attendance/login_selection.html')

def admin_login(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'attendance/admin_login.html')

def student_login(request):
    if request.method == 'POST':
        identifier = request.POST.get('username')
        password = request.POST.get('password')
        user = None
        if '@' in identifier:
            try:
                u = User.objects.get(email=identifier)
                user = authenticate(request, username=u.username, password=password)
            except User.DoesNotExist:
                pass
        else:
            user = authenticate(request, username=identifier, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'attendance/student_login.html', {'error': 'Invalid login'})
            
    return render(request, 'attendance/student_login.html')

def signout_view(request):
    logout(request)
    return redirect('home')

def admin_logout(request):
    logout(request)
    return redirect('home') 

def dashboard(request):
    total_students = User.objects.filter(is_superuser=False).count()
    context = {
        'total_students': total_students,
        'present_today': 0 
    }
    return render(request, 'attendance/dashboard.html', context)

@login_required
def set_password(request):
    if request.method == 'POST':
        p1 = request.POST.get('password')
        p2 = request.POST.get('confirm_password')
        
        if p1 == p2:
            u = request.user 
            u.set_password(p1) 
            u.save()
            update_session_auth_hash(request, u)
            return redirect('home')
            
    return render(request, 'attendance/set_password.html')
        
@receiver(user_signed_up)
def google_signup_redirect(sender, request, user, **kwargs):
    return redirect('set_password')

@login_required
def admin_dashboard(request):
    departments = Department.objects.all()
    subjects = Subject.objects.all()
    active_session = AttendanceSession.objects.filter(admin=request.user, status='active').last()
    
    present_students = []
    if active_session:
        present_students = active_session.records.all().order_by('-timestamp')

    context = {
        'departments': departments,
        'subjects': subjects,
        'active_session': active_session,
        'present_students': present_students,
    }
    return render(request, 'attendance/admin_dashboard.html', context)

def stop_session(request):
    active_session = AttendanceSession.objects.filter(admin=request.user, status='active').last()
    if active_session:
        active_session.status = 'completed'
        active_session.save()
    return redirect('admin_dashboard')

def start_session(request):
    if request.method == "POST":
        subject_id = request.POST.get('subject')
        subject = Subject.objects.get(id=subject_id)
        
        
        lat = request.POST.get('admin_lat')
        lng = request.POST.get('admin_long')
        
        today = timezone.now().date()
      
        existing_sessions_today = AttendanceSession.objects.filter(date=today)
        
        if existing_sessions_today.exists():
            current_day = existing_sessions_today.first().day_number
        else:
            last_session = AttendanceSession.objects.order_by('-date').first()
            current_day = (last_session.day_number + 1) if last_session else 1

      
        next_session_num = AttendanceSession.objects.filter(date=today).count() + 1

        AttendanceSession.objects.create(
            subject=subject,
            admin=request.user,
            day_number=current_day,
            session_number=next_session_num,
            admin_lat=lat,
            admin_long=lng,
            status='active'
        )
    return redirect('admin_dashboard')

def get_live_scans(request, session_id):
    records = AttendanceRecord.objects.filter(session_id=session_id).order_by('-timestamp')
    data = [
        {
            "name": r.student.username, 
            "id": r.student.id,
            "time": r.timestamp.strftime('%H:%M:%S') 
        } 
        for r in records
    ]
    return JsonResponse({"students": data})

@login_required
def mark_manual_attendance(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id')
            session_id = data.get('session_id')
            
           
            student = User.objects.get(id=student_id)
            session = AttendanceSession.objects.get(id=session_id)
            
            AttendanceRecord.objects.get_or_create(
                session=session,
                student=student,
                defaults={
                    'student_lat': session.admin_lat, 
                    'student_long': session.admin_long
                }
            )
            return JsonResponse({"status": "success"})
        except User.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Student record not found."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
            
    return JsonResponse({"status": "error", "message": "Invalid Request"})

@login_required
def admin_dashboard(request):
    departments = Department.objects.all()
    subjects = Subject.objects.all()
    
    active_session = AttendanceSession.objects.filter(admin=request.user, status='active').order_by('-id').first()
    
    present_students = []
    if active_session:
       
        present_students = active_session.records.all().order_by('-timestamp')

    all_students = User.objects.filter(is_superuser=False) 

    context = {
        'departments': departments,
        'subjects': subjects,
        'active_session': active_session,
        'present_students': present_students,
        'all_students': all_students,
    }
    return render(request, 'attendance/admin_dashboard.html', context)

@login_required
def daily_logs_view(request):
    
    sessions = AttendanceSession.objects.filter(admin=request.user).order_by('-date', '-session_number')
    return render(request, 'attendance/daily_logs.html', {'sessions': sessions})

@login_required
def archive_today(request):
    if request.method == "POST":
        today = timezone.now().date()
    
        AttendanceSession.objects.filter(
            admin=request.user, 
            date=today, 
            status='active'
        ).update(status='archived')
    return redirect('daily_logs')

def students_list_view(request):
    students = User.objects.all().order_by('username') 
    return render(request, 'attendance/students_list.html', {'students': students})