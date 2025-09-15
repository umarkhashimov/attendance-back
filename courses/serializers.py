from rest_framework import serializers
from .models import CourseModel, SubjectModel
from users.serializers import TeacherModelSerializer
from students.serializers import EnrollmentModelSerializer

class SubjectModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectModel
        fields = '__all__'

class CourseModelListSerializer(serializers.ModelSerializer):
    subject = SubjectModelSerializer(read_only=True)
    teacher = TeacherModelSerializer(read_only=True)
    name_weekdays = serializers.CharField(source='get_name', read_only=True)
    enrolled_count = serializers.IntegerField(source='get_enrolled_count', read_only=True)
    individual = serializers.IntegerField(source='is_individual', read_only=True)
    single_enrollment = EnrollmentModelSerializer(source='get_single_enrollment', read_only=True)

    class Meta:
        model = CourseModel
        exclude = ['enrolled']

