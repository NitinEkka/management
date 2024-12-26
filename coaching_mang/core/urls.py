from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.custom_login, name='custom_login'),
    path('logout/', views.custom_logout, name='custom_logout'),
    path('register/', views.register, name='register_page'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('create-course/', views.create_course, name='create_course'),
]
