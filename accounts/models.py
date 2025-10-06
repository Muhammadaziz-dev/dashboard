from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        TEACHER = 'TEACHER', 'Teacher'
        STUDENT = 'STUDENT', 'Student'

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.STUDENT,
    )

    def save(self, *args, **kwargs):
        # Ensure superusers and ADMIN role always have admin-site access
        if self.is_superuser or self.role == self.Roles.ADMIN:
            self.is_staff = True
        # Do not forcibly set is_staff False for other roles; keep whatever is set.
        super().save(*args, **kwargs)


class Lesson(models.Model):
    title = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0, db_index=True)
    # Optional calendar date for the lesson to support join-date logic
    date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.order + 1}: {self.title}"


class Student(models.Model):
    class Levels(models.TextChoices):
        A0 = 'A0', 'A0'
        A1 = 'A1', 'A1'
        A2 = 'A2', 'A2'
        B1 = 'B1', 'B1'
        B2 = 'B2', 'B2'
        C1 = 'C1', 'C1'

    name = models.CharField(max_length=120, blank=True, default="")
    level = models.CharField(max_length=2, choices=Levels.choices)
    note = models.CharField(max_length=255, blank=True, default="")
    # Track when a student joined to exclude earlier lessons from stats
    joined_at = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.name or '—'} ({self.level})"


class Record(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='records')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='records')
    class Attendance(models.TextChoices):
        PRESENT = 'P', '+'
        EXCUSED = 'E', '−'
        ABSENT = 'A', '×'

    attendance = models.CharField(max_length=1, choices=Attendance.choices, default=Attendance.ABSENT)
    homework = models.BooleanField(default=False)
    extra = models.CharField(max_length=255, blank=True, default="")
    test_score = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("student", "lesson")
