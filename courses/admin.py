from django.contrib import admin
from .models import Subject, Course, Module
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    search_fields = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}

class ModuleInline(admin.StackedInline):
    model = Module
    

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'owner', 'students_count', 'created']
    list_filter = ['created', 'subject', 'owner']
    search_fields = ['title', 'overview', 'owner__email', 'owner__first_name', 'owner__last_name']
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ('subject', 'owner')
    list_select_related = ('subject', 'owner')
    date_hierarchy = 'created'
    inlines = [ModuleInline]

    def students_count(self, obj):
        return obj.students.count()
    students_count.short_description = 'Students'

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'slug']
    list_editable = ('order',)
    list_filter = ['course']
    search_fields = ['title', 'slug', 'course__title']
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ('course',)
    list_select_related = ('course',)
