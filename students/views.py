from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CourseEnrollForm
from django.views.generic.list import ListView
from courses.models import Course
from django.views.generic.detail import DetailView
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views import View
from django.db.models import Prefetch, Count





class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    course = None
    form_class = CourseEnrollForm
    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        messages.success(self.request, f'You enrolled in “{self.course.title}”.')
        return super().form_valid(form)
    def get_success_url(self):
        return reverse_lazy('students:student_course_detail', args=[self.course.slug])
    
class StudentUnenrollCourseView(LoginRequiredMixin, View):
    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug, students=request.user)
        course.students.remove(request.user)
        messages.info(request, f'You unenrolled from “{course.title}”.')
        return redirect('students:student_course_list')
    

class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/course/list.html'
    extra_context = {'title': 'My enrolled courses'}
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user]).select_related('subject', 'owner').prefetch_related('modules').annotate(total_modules=Count('modules', distinct=True), total_students=Count('students', distinct=True))
    
class StudentCourseDetailView(DetailView):
    model = Course
    template_name = 'students/course/detail.html'
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user]).select_related('subject', 'owner').prefetch_related(
                'modules',
                Prefetch('modules__contents')  
            )
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        slug = self.kwargs.get('module_slug')
        if slug:
            context['module'] = get_object_or_404(course.modules, slug=slug)
        else:
            context['module'] = course.modules.first()
        context['title'] = f'{course.title} — my course'
        return context