from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_selection, name='login_selection'),  
    path('login/admin/', views.admin_login, name='admin_login'),
    path('login/student/', views.student_login, name='student_login'), 
    path('logout/', views.admin_logout, name='admin_logout'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('set-password/', views.set_password, name='set_password'),
    path('start-session/', views.start_session, name='start_session'),
    path('stop-session/', views.stop_session, name='stop_session'),
    path('submit-attendance/', views.submit_attendance, name='submit_attendance'),
    path('mark-manual-attendance/', views.mark_manual_attendance, name='mark_manual_attendance'),
    path('daily-logs/', views.daily_logs_view, name='daily_logs'),
    path('archive-today/', views.archive_today, name='archive_today'), 
    path('students/', views.students_list_view, name='students_list'),
]