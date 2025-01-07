from rest_framework import serializers
from users.models import *

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [ 'title', 'description', 'level', 'field_of_study']
        

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['title', 'course', 'video_url', 'video_file', 
                  'pdf', 'content', 'order', 'homework_requirements']
        

class StudentAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAssignment
        fields = '__all__'