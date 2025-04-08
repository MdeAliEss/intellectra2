# courses/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, CategoryViewSet

router = DefaultRouter(trailing_slash=True)
router.register(r'categories', CategoryViewSet)
router.register(r'courses', CourseViewSet)

urlpatterns = [ 
    path('api/', include(router.urls)),
]
