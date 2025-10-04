from rest_framework import serializers

from .models import User, Lesson, Student, Record


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
        ]


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "order", "date"]


class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = ["attendance", "homework", "extra", "test_score"]


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["id", "name", "level", "note", "joined_at"]


class DashboardStateSerializer(serializers.Serializer):
    lessons = LessonSerializer(many=True)
    students = serializers.DictField(child=StudentSerializer(many=True))  # keys: A2/B1/B2
    # records: mapping of student_id -> lesson_id -> record fields
    records = serializers.DictField(child=serializers.DictField(child=RecordSerializer()))
