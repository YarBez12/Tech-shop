from django.views.generic.list import ListView
from .models import Course
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet
from django.forms.models import modelform_factory
from django.apps import apps
from .models import Module, Content, Subject
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.db.models import Count
from django.views.generic.detail import DetailView
from students.forms import CourseEnrollForm
from django.core.cache import cache
from django.utils.http import url_has_allowed_host_and_scheme
from django.db import transaction



class OwnerMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return (qs.filter(owner=self.request.user)
                  .select_related('owner', 'subject'))
class OwnerEditMixin:
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin):
    model = Course
    fields = ['subject', 'title', 'overview']
    success_url = reverse_lazy('courses:manage_course_list')
class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'
class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
    extra_context = {
        'title': 'My courses'
    }

    def get_queryset(self):
        return (super().get_queryset()
                .annotate(
                    total_modules=Count('modules', distinct=True),
                    total_students=Count('students', distinct=True),
                )
                .only('id', 'title', 'slug', 'overview', 'created', 'subject', 'owner'))
class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'
    extra_context = {
        'title': 'Create a new course'
    }

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Course '{self.object.title}' has been created successfully!")
        return response
class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next') or self.request.POST.get('next', '')
        context['title'] = f"Edit course '{self.object.title}'"
        return context
    def get_success_url(self):
        redirect_page = self.request.POST.get('next') or self.request.GET.get('next')
        if redirect_page and url_has_allowed_host_and_scheme(redirect_page, allowed_hosts={self.request.get_host()}):
            return redirect_page
        return super().get_success_url()
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Course '{self.object.title}' has been updated successfully!")
        return response
class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Delete course '{self.object.title}'"
        return context

    def get_success_url(self):
        messages.warning(self.request, f"Course '{self.object.title}' has been deleted!", extra_tags='deleted')
        return reverse_lazy('courses:manage_course_list')
    

class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None
    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)
    def dispatch(self, request, slug):
        self.course = get_object_or_404(
            Course.objects.only('id', 'title', 'slug').filter(owner=request.user),
            slug=slug
        )
        return super().dispatch(request, slug)
    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({
            "title": f"Manage modules for '{self.course.title}'",
            "course": self.course,
            "formset": formset,
        })
    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(request, f"Modules for '{self.course.title}' have been updated!")
            return redirect('courses:manage_course_list')
        return self.render_to_response({
                                    'course': self.course,
                                    'formset': formset})
    


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'
    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses',
                                model_name=model_name)
        return None
    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner',
                                                'order',
                                                'created',
                                                'updated'])
        return Form(*args, **kwargs)
    def dispatch(self, request, module_slug, model_name, id=None):
        self.module = get_object_or_404(Module,
                                        slug=module_slug,
                                        course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,
                                        pk=id,
                                        owner=request.user)
        return super().dispatch(request, module_slug, model_name, id)
    
    def get(self, request, module_slug, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({
            "title": f"{'Edit' if id else 'Create'} {model_name.capitalize()} for '{self.module.title}'",
            "form": form,
            "object": self.obj
        })
    def post(self, request, module_slug, model_name, id=None):
        form = self.get_form(self.model,
                            instance=self.obj,
                            data=request.POST,
                            files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                Content.objects.create(module=self.module,
                                        item=obj)
                messages.success(request, f"New {model_name} added to '{self.module.title}'!")
            else:
                messages.success(request, f"{model_name.capitalize()} has been updated!")
            return redirect('courses:module_content_list', self.module.slug)
        return self.render_to_response({'form': form,
        'object': self.obj})
    

class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content,
                                    pk=id,
                                    module__course__owner=request.user)
        module = content.module
        item_str = str(content.item)
        content.item.delete()
        content.delete()
        messages.warning(request, f"Content '{item_str}' has been deleted!")
        return redirect('courses:module_content_list', module.slug)
    
class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'
    def get(self, request, module_slug):
        module = get_object_or_404(
            Module.objects.select_related('course'),
            slug=module_slug,
            course__owner=request.user
        )
        return self.render_to_response({
            "title": f"Contents of '{module.title}'",
            "module": module
        })
    

class ModuleOrderView(CsrfExemptMixin,
                    JsonRequestResponseMixin,
                    View):
    def post(self, request):
        order_map = {int(id): order for id, order in self.request_json.items()}
        if not order_map:
            return self.render_json_response({'saved': 'OK'})
        ids = list(order_map.keys())
        with transaction.atomic():
            modules = list(Module.objects.filter(id__in=ids, course__owner=request.user))
            for module in modules:
                module.order = order_map.get(module.id, module.order)
            Module.objects.bulk_update(modules, ['order'])
        return self.render_json_response({'saved': 'OK'})
    
class ContentOrderView(CsrfExemptMixin,
                    JsonRequestResponseMixin,
                    View):
    def post(self, request):
        order_map = {int(id): order for id, order in self.request_json.items()}
        if not order_map:
            return self.render_json_response({'saved': 'OK'})
        ids = list(order_map.keys())
        with transaction.atomic():
            contents = list(Content.objects.filter(id__in=ids, module__course__owner=request.user))
            for content in contents:
                content.order = order_map.get(content.id, content.order)
            Content.objects.bulk_update(contents, ['order'])
        return self.render_json_response({'saved': 'OK'})
    
class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'courses/course/list.html'
    def get(self, request, subject_slug=None):
        subjects = cache.get('all_subjects')
        if not subjects:
            subjects = (Subject.objects
                        .annotate(total_courses=Count('courses', distinct=True))
                        .only('id', 'title', 'slug'))
            cache.set('all_subjects', subjects, timeout=60)
        all_courses = (Course.objects
                .select_related('subject', 'owner')
                .annotate(total_modules=Count('modules', distinct=True),
                          total_students=Count('students', distinct=True))
                .only('id', 'title', 'slug', 'overview', 'created', 'subject', 'owner'))
        subject = None
        if subject_slug:
            subject = get_object_or_404(Subject, slug=subject_slug)
            key = f'subject_{subject.id}_courses'
            courses = cache.get(key)
            if not courses:
                courses = all_courses.filter(subject=subject)
                cache.set(key, courses, timeout=60)
        else:
            courses = cache.get('all_courses')
            if not courses:
                courses = all_courses
                cache.set('all_courses', courses, timeout=60)
        return self.render_to_response({
            "title": subject.title if subject else "All Courses",
            "subjects": subjects,
            "subject": subject,
            "courses": courses
        })
    

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        context['enroll_form'] = CourseEnrollForm(initial={'course':self.object})
        context["title"] = self.object.title
        context['is_enrolled'] = (
            self.request.user.is_authenticated and
            course.students.filter(pk=self.request.user.pk).exists()
        )
        context['first_module'] = course.modules.first()
        return context
    
    def get_queryset(self):
        return (Course.objects
                .select_related('owner', 'subject')
                .prefetch_related('modules', 'students'))