from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.utils.html import format_html
from .models import *

# Inline for Student and Staff creation inside admin
class StudentInline(admin.TabularInline):
    model = Student
    extra = 0
    fields = ('user', 'roll_no', 'fee_paid', 'total_fee')
    readonly_fields = ('user', 'roll_no')
    can_delete = False

class StaffInline(admin.TabularInline):
    model = Staff
    extra = 0
    fields = ('user', 'salary', 'courses')
    readonly_fields = ('user',)
    can_delete = False


# Custom Admin to manage User Roles (student/staff/admin)
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'get_role')
    search_fields = ('username', 'email')

    def get_role(self, obj):
        return obj.role
    get_role.short_description = 'Role'

    # def save_model(self, request, obj, form, change):
    #     if 'admin' in request.POST:  # If the admin is creating a user, assign a group
    #         role = request.POST.get('role', None)
    #         if role:
    #             group = Group.objects.get(name=role)
    #             obj.groups.add(group)
    #     super().save_model(request, obj, form, change)
    def save_model(self, request, obj, form, change):
        """
        Save the user and create related Student or Staff instance based on role.
        """
        super().save_model(request, obj, form, change)

        # Check the role and create related model instance if not exists
        if obj.role == 'student':
            Student.objects.get_or_create(user=obj)
        elif obj.role == 'staff':
            Staff.objects.get_or_create(user=obj)

    def get_model_perms(self, request):
        """
        Allow full permissions for superusers. Restrict others based on group.
        """
        if request.user.is_superuser:
            # Superusers should have all permissions
            return {
                'add': True,
                'change': True,
                'delete': True,
                'view': True,
            }
        elif request.user.groups.filter(name='admin').exists():
            # Admins should also have all permissions
            return {
                'add': True,
                'change': True,
                'delete': True,
                'view': True,
            }
        # Default to no permissions
        return {
            'add': False,
            'change': False,
            'delete': False,
            'view': False,
        }


# Course Admin to control which sections are accessible
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'total_students', 'total_staff')
    search_fields = ('name',)
    inlines = [StudentInline]
    filter_horizontal = ('staff_members',)

    def get_model_perms(self, request):
        """
        Allow full permissions for superusers. Restrict others based on group.
        """
        if request.user.is_superuser:
            # Superusers should have all permissions
            return {
                'add': True,
                'change': True,
                'delete': True,
                'view': True,
            }
        elif request.user.groups.filter(name='admin').exists():
            # Admins should also have all permissions
            return {
                'add': True,
                'change': True,
                'delete': True,
                'view': True,
            }
        # Default to no permissions
        return {
            'add': False,
            'change': False,
            'delete': False,
            'view': False,
        }


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'roll_no', 'course', 'fee_paid', 'total_fee', 'fee_due')
    search_fields = ('user__username', 'student_id', 'roll_no')
    list_filter = ('course',)
    exclude = ('student_id',)

    def save_model(self, request, obj, form, change):
        """
        Ensure the related User role is set to student.
        """
        if obj.user:
            obj.user.role = 'student'
            obj.user.save()
        super().save_model(request, obj, form, change)

    def get_model_perms(self, request):
        """
        Allow full permissions for superusers. Restrict others based on group.
        """
        if request.user.is_superuser:
            # Superusers should have all permissions
            return {
                'add': True,
                'change': True,
                'delete': True,
                'view': True,
            }
        elif request.user.groups.filter(name='admin').exists():
            # Admins should also have all permissions
            return {
                'add': True,
                'change': True,
                'delete': True,
                'view': True,
            }
        # Default to no permissions
        return {
            'add': False,
            'change': False,
            'delete': False,
            'view': False,
        }


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'salary', 'courses_display')
    search_fields = ('user__username',)
    list_filter = ('courses',)

    def save_model(self, request, obj, form, change):
        """
        Ensure the related User role is set to staff.
        """
        if obj.user:
            obj.user.role = 'staff'
            obj.user.save()
        super().save_model(request, obj, form, change)

    def get_model_perms(self, request):
        """
        Allow full permissions for superusers. Restrict others based on group.
        """
        if request.user.is_superuser:
            return {
                'add': True,
                'change': True,
                'delete': True,
                'view': True,
            }
        elif request.user.groups.filter(name='admin').exists():
            return {
                'add': True,
                'change': True,
                'delete': True,
                'view': True,
            }
        return {
            'add': False,
            'change': False,
            'delete': False,
            'view': False,
        }

    def courses_display(self, obj):
        """
        Custom method to display the course names associated with the staff member.
        """
        return ", ".join([course.name for course in obj.courses.all()])

    courses_display.short_description = 'Courses' 


# Fee and Salary Management
class FeeAndSalaryAdminSite(admin.AdminSite):
    site_header = "Fee and Salary Management"
    site_title = "Management"
    index_title = "Welcome to the Management Portal"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('fee_due_students/', self.admin_view(self.fee_due_students)),
        ]
        return custom_urls + urls

    def fee_due_students(self, request):
        students = Student.objects.filter(total_fee__gt=models.F('fee_paid'))
        rows = "".join(
            f"<tr><td>{s.user.username}</td><td>{s.fee_due()}</td></tr>" for s in students
        )
        return format_html(f"<table><tr><th>Student Name</th><th>Due Fee</th></tr>{rows}</table>")

# Custom admin site for Fee and Salary
admin_site = FeeAndSalaryAdminSite(name='management')
admin_site.register(User, UserAdmin)
admin_site.register(Course, CourseAdmin)
admin_site.register(Student, StudentAdmin)
admin_site.register(Staff, StaffAdmin)

