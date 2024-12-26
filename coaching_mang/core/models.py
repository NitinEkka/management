from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='admin')

    # Override the related_name to avoid clash with the default User model
    # groups = models.ManyToManyField(
    #     'auth.Group', 
    #     related_name='core_user_set',  # Use a custom related_name
    #     blank=True
    # )
    # user_permissions = models.ManyToManyField(
    #     'auth.Permission',
    #     related_name='core_user_permissions_set',  # Use a custom related_name
    #     blank=True
    # )

    def save(self, *args, **kwargs):
        if self.is_superuser:  # Ensure superuser has correct role
            self.role = 'admin'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    staff_members = models.ManyToManyField('Staff', related_name='assigned_courses', blank=True)  # Use a unique related_name

    def total_students(self):
        return Student.objects.filter(course=self).count()

    def total_staff(self):
        return self.staff_members.count()

    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', null=True, blank=True)
    student_id = models.CharField(max_length=10, unique=True, blank=True) 
    roll_no = models.PositiveIntegerField(unique=True, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    fee_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    total_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)

    def fee_due(self):
        return self.total_fee - self.fee_paid

    def generate_student_id(self):
        while True:
            student_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not Student.objects.filter(student_id=student_id).exists():
                return student_id

    def save(self, *args, **kwargs):
        if not self.student_id:
            self.student_id = self.generate_student_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.student_id})"


class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile', null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    courses = models.ManyToManyField(Course, related_name='staff_courses', blank=True)

    def __str__(self):
        return self.user.username
