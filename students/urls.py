from django.urls import path
from .views import *
from django.views.decorators.cache import cache_page

app_name = 'students'

urlpatterns = [
    path('enroll-course/', StudentEnrollCourseView.as_view(), name='student_enroll_course'),
    path('<slug:slug>/course-unenroll/', StudentUnenrollCourseView.as_view(), name='student_unenroll_course'),
    path('courses/', StudentCourseListView.as_view(), name='student_course_list'),
    path('course/<slug:slug>/', StudentCourseDetailView.as_view(), name='student_course_detail'),
    path('course/<slug:slug>/<slug:module_slug>/', StudentCourseDetailView.as_view(), name='student_course_detail_module'),
]