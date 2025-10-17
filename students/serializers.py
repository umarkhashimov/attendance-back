from rest_framework import serializers
from .models import Enrollment, StudentModel

class StudentSerializer(serializers.ModelSerializer):
    has_debt = serializers.BooleanField(source='in_debt', read_only=True)
    status = serializers.BooleanField(source='get_status', read_only=True)


    class Meta:
        model = StudentModel
        fields = '__all__'

class EnrollmentModelSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    current_balance = serializers.IntegerField(source='balance', read_only=True)

    class Meta:
        model = Enrollment
        fields = '__all__'