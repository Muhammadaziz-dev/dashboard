from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.authentication import SessionAuthentication

from .serializers import (
    UserSerializer,
    DashboardStateSerializer,
    LessonSerializer,
    StudentSerializer,
    RecordSerializer,
)
from .models import User, Lesson, Student, Record


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user: User = self.request.user
        ctx["can_edit"] = bool(
            user.is_superuser or user.role in [User.Roles.ADMIN, User.Roles.TEACHER]
        )
        return ctx


class IsAdminOrTeacher(BasePermission):
    def has_permission(self, request, view):
        user: User = request.user
        if not user.is_authenticated:
            return False
        return user.role in [User.Roles.ADMIN, User.Roles.TEACHER] or user.is_superuser


class DashboardStateView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Seed defaults on first run: 24 lessons and 30 students for each level
        if Lesson.objects.count() == 0:
            for i in range(24):
                Lesson.objects.create(title=f"{i+1}-dars", order=i)
        for level in [Student.Levels.A2, Student.Levels.B1, Student.Levels.B2]:
            if not Student.objects.filter(level=level).exists():
                Student.objects.bulk_create([Student(level=level, name="") for _ in range(30)])

        lessons = Lesson.objects.all()
        students_by_level = {
            'A2': list(Student.objects.filter(level=Student.Levels.A2)),
            'B1': list(Student.objects.filter(level=Student.Levels.B1)),
            'B2': list(Student.objects.filter(level=Student.Levels.B2)),
        }

        # Build records map: student_id -> lesson_id -> data
        records_map = {}
        recs = Record.objects.select_related('student', 'lesson').all()
        for r in recs:
            sid = str(r.student_id)
            lid = str(r.lesson_id)
            records_map.setdefault(sid, {})[lid] = {
                'attendance': r.attendance,
                'homework': r.homework,
                'extra': r.extra,
                'test_score': r.test_score,
            }

        data = {
            'lessons': LessonSerializer(lessons, many=True).data,
            'students': {
                'A2': StudentSerializer(students_by_level['A2'], many=True).data,
                'B1': StudentSerializer(students_by_level['B1'], many=True).data,
                'B2': StudentSerializer(students_by_level['B2'], many=True).data,
            },
            'records': records_map,
        }
        return Response(DashboardStateSerializer(data).data)


class DashboardSaveView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]

    @transaction.atomic
    def post(self, request):
        payload = request.data
        # Expected payload: { records: { student_id: { lesson_id: {attendance,homework,extra,test_score}}}, students: [ {id,name,note} ] }
        records = payload.get('records', {})
        # Upsert records
        for sid, lessons in records.items():
            for lid, r in lessons.items():
                obj, _ = Record.objects.get_or_create(student_id=sid, lesson_id=lid)
                ser = RecordSerializer(instance=obj, data=r, partial=True)
                ser.is_valid(raise_exception=True)
                ser.save()

        # Update students basic info if provided
        students_update = payload.get('students', [])
        for s in students_update:
            if 'id' in s:
                Student.objects.filter(id=s['id']).update(name=s.get('name', ''), note=s.get('note', ''))

        return Response({"status": "ok"})


class DashboardClearView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]

    @transaction.atomic
    def post(self, request):
        Record.objects.all().delete()
        # Also clear student names and notes as requested
        Student.objects.all().update(name="", note="")
        return Response({"status": "cleared_all"})


class LessonAddView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]

    def post(self, request):
        count = Lesson.objects.count()
        lesson = Lesson.objects.create(title=f"{count+1}-dars", order=count)
        return Response(LessonSerializer(lesson).data)


class LessonRemoveView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]

    @transaction.atomic
    def post(self, request):
        # Enforce a minimum number of lessons kept
        MIN_LESSONS = 3
        if Lesson.objects.count() <= MIN_LESSONS:
            return Response({"status": "min_reached", "min": MIN_LESSONS})
        last = Lesson.objects.order_by('-order', '-id').first()
        if not last:
            return Response({"status": "noop"})
        Record.objects.filter(lesson=last).delete()
        last.delete()
        return Response({"status": "removed"})
