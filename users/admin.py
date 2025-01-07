from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Prerequisite)
admin.site.register(FieldOfStudy)
admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Enrollment)
admin.site.register(StudentAssignment)
admin.site.register(LessonCompletion)
admin.site.register(Quiz)
admin.site.register(Answer)
admin.site.register(StudentAnswer)
admin.site.register(StudentQuizSession)
admin.site.register(Notification)

# To have an opportunity to add answers in the same window as questions

class AnswerInLine(admin.TabularInline):
    model = Answer

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInLine]

admin.site.register(Question, QuestionAdmin)
