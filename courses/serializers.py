# serializers.py
from rest_framework import serializers
from .models import Course, Category, CourseSection, CoursePdfInternal 

class CourseSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSection
        fields = ['id', 'title', 'content', 'order']  # Adjust fields as necessary

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
            'id', 'title', 'description', 'pdfs', 'videos', 'image', 'file_type', 'duration', 'rating', 'created_at', 
            'professor', 'category', 'pdf_internal_data', 'quizzes'
        ]
    def validate_quizzes(self, value):
        for quiz in value:
            if 'question' not in quiz or 'answers' not in quiz or 'correct_index' not in quiz:
                raise serializers.ValidationError("Each quiz must have 'question', 'answers', and 'correct_index'")
            if len(quiz['answers']) < 2:
                raise serializers.ValidationError("Each quiz must have at least two answers.")
            if quiz['correct_index'] >= len(quiz['answers']):
                raise serializers.ValidationError("correct_index must be a valid index in answers.")
        return value

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'