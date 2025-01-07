from django import forms
from users.models import Course, Lesson
from django.forms.widgets import ClearableFileInput

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'level', 'field_of_study', 'prerequisites']

# Change default label name to custom one
class CustomClearableFileInput(ClearableFileInput):
    clear_checkbox_label = "Remove"

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'order', 'content', 'video_url', 'video_file', 'pdf', 
                  'homework_requirements']
        widgets = {
            'video_file': CustomClearableFileInput(),
            'pdf': CustomClearableFileInput(),
        }

    # Pass the course as a hidden field in the form, since Lesson always belongs to specific course
    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        if course:
            self.fields['course'].initial = course

        
