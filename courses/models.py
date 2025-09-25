from django.db import models
from users.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .fields import OrderField
from django.utils.text import slugify
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError



class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    class Meta:
        ordering = ['title']
        indexes = [models.Index(fields=['slug'])]
    def __str__(self):
        return self.title
class Course(models.Model):
    owner = models.ForeignKey(User, related_name='courses_created', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, related_name='courses', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(User, related_name='courses_joined', blank=True)
    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['subject', 'created']),
        ]
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            candidates = Course.objects.filter(slug__startswith=base).values_list('slug', flat=True)
            existing = set(candidates)
            slug = base
            i = 1
            while slug in existing:
                slug = f'{base}-{i}'
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['course'])

    def __str__(self):
        prefix = f'{self.order}. ' if self.order is not None else ''
        return f'{prefix}{self.title}'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            unique = base
            num = 1
            while Module.objects.filter(course=self.course, slug=unique).exists():
                unique = f'{base}-{num}'
                num += 1
            self.slug = unique
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['order']
        indexes = [models.Index(fields=['course', 'order'])]
        constraints = [
            models.UniqueConstraint(fields=['course', 'slug'], name='module_slug_unique_per_course'),
        ]

    

class Content(models.Model):
    module = models.ForeignKey(Module, related_name='contents', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, 
                                     limit_choices_to={'model__in':(
                                         'text',
                                         'video',
                                         'image',
                                         'file')})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])

    def clean(self):
        super().clean()
        if hasattr(self.item, 'owner'):
            if self.item.owner_id != self.module.course.owner_id:
                raise ValidationError('Owner of item must match course owner.')

    class Meta:
        ordering = ['order']
        indexes = [models.Index(fields=['module', 'order'])]


class ItemBase(models.Model):
    owner = models.ForeignKey(User, related_name='%(class)s_related', on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
    def __str__(self):
        return self.title
    
    def render(self):
        return render_to_string(f'courses/content/{self._meta.model_name}.html', {'item': self})
class Text(ItemBase):
    content = models.TextField()
class File(ItemBase):
    file = models.FileField(upload_to='learning_files')
class Image(ItemBase):
    file = models.FileField(upload_to='learning_images')
class Video(ItemBase):
    url = models.URLField()


