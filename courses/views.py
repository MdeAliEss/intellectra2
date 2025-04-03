from .models import Category, Course
from .serializers import CategorySerializer, CourseSerializer
from rest_framework import viewsets

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all() 
    serializer_class = CourseSerializer

    def perform_create(self, serializer):
        course = serializer.save()
        # Additional logic to handle PDF and video processing can go here
        if course.pdfs:
            # Process PDF file
            pass
        if course.videos:
            # Process video file
            pass