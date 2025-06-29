from django.urls import path
from .views import *

app_name = 'courses'

urlpatterns = [
    path('mine/', ManageCourseListView.as_view(), name='manage_course_list'),
    path('create/', CourseCreateView.as_view(), name='course_create'),
    path('<slug:slug>/edit/', CourseUpdateView.as_view(), name='course_edit'),
    path('<slug:slug>/delete/', CourseDeleteView.as_view(), name='course_delete'),
    path('<slug:slug>/module/', CourseModuleUpdateView.as_view(), name='course'),
    path('module/<slug:module_slug>/content/<model_name>/create/', ContentCreateUpdateView.as_view(), name='module_content_create'),
    path('module/<slug:module_slug>/content/<model_name>/<int:id>/', ContentCreateUpdateView.as_view(), name='module_content_update'),
    path('content/<int:id>/delete/', ContentDeleteView.as_view(), name='module_content_delete'),
    path('module/order/', ModuleOrderView.as_view(), name='module_order'),
    path('module/<slug:module_slug>/', ModuleContentListView.as_view(), name='module_content_list'),
    path('content/order/', ContentOrderView.as_view(), name='content_order'),
    path('subject/<slug:subject_slug>/', CourseListView.as_view(), name='course_list_subject'),
    path('<slug:slug>/', CourseDetailView.as_view(), name='course_detail'),
    path('', CourseListView.as_view(), name='course_list'),
]