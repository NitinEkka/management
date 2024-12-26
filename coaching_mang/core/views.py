from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User, Course
from .forms import UserRegistrationForm, CourseForm

# Login View
def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('register_page')  # Redirect to registration page if admin
            elif user.role == 'student':
                return redirect('student_dashboard')  # Redirect to student dashboard
            elif user.role == 'staff':
                return redirect('staff_dashboard')  # Redirect to staff dashboard
            else:
                messages.error(request, 'User role not recognized.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'core/login.html')

# Register View (Only for Superuser)
@login_required
def register(request):
    if not request.user.is_superuser:
        return redirect('custom_login')  # Redirect non-admin users to login page

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create and save the user object
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash the password
            user.save()
            messages.success(request, f"User {user.username} has been registered successfully!")
            return redirect('register_page')  # Stay on the registration page after successful registration
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()

    return render(request, 'core/register.html', {'form': form})

# Logout View
def custom_logout(request):
    logout(request)
    return redirect('custom_login')  # Redirect to login page after logout

# Student Dashboard
@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('custom_login')  # Ensure only students can access this view
    return render(request, 'core/student_dashboard.html')

# Staff Dashboard
@login_required
def staff_dashboard(request):
    if request.user.role != 'staff':
        return redirect('custom_login')  # Ensure only staff can access this view
    return render(request, 'core/staff_dashboard.html')


def create_course(request):
    if not request.user.is_superuser:
        return redirect('custom_login')  # Ensure only admin can access this view
    
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course created successfully!')
            return redirect('create_course')  # Stay on the create course page after creation
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CourseForm()

    return render(request, 'core/create_course.html', {'form': form})