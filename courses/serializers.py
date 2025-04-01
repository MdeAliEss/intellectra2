from rest_framework import serializers
from .models import Course, Category, CourseSection, CoursePdfInternal

class CourseSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSection
        exclude = ['pdf_data']

class CoursePdfInternalSerializer(serializers.ModelSerializer):
    sections = CourseSectionSerializer(many=True, read_only=True)

    class Meta:
        model = CoursePdfInternal
        fields = ['id', 'name', 'table_of_contents', 'sections']
        read_only_fields = ['name', 'table_of_contents', 'sections']

class CourseSerializer(serializers.ModelSerializer):
    pdf_internal_data = CoursePdfInternalSerializer(read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'file', 'image', 'file_type',
            'duration', 'rating', 'created_at', 'professor', 'category',
            'pdf_internal_data'
        ]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'




