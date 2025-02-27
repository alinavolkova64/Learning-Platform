from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from capstone.storage_backends import MediaStorage  # Import custom storage


class User(AbstractUser):
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    

class FieldOfStudy(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Field of Studies"


class Prerequisite(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Course(models.Model):
    # Represents a course that an instructor can create and students can enroll in.
    title = models.CharField(max_length=150)
    description = models.TextField()
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses')
    
    LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True, null=True)
    field_of_study = models.ForeignKey(FieldOfStudy, on_delete=models.CASCADE, default=1)
    prerequisites = models.ManyToManyField(Prerequisite)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} course"


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    video_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(storage=MediaStorage(), upload_to='lesson_videos/', blank=True, null=True)
    pdf = models.FileField(storage=MediaStorage(), upload_to='lesson_pdfs/', blank=True, null=True)
    content = models.TextField() 
    order = models.PositiveIntegerField()  # Order of lessons in a course
    homework_requirements = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} (Order: {self.order}, Course: {self.course.title})"  
    

class Enrollment(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    date_enrolled = models.DateTimeField(auto_now_add=True)
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # progress percentage
    completed_lessons = models.ManyToManyField(Lesson, through='LessonCompletion')
    
    def calculate_progress(self):
        # Count completed lessons associated with this Enrollment instance
        completed_lessons = LessonCompletion.objects.filter(enrollment=self).count()
        # Total lessons for the course associated with this Enrollment instance
        total_lessons = self.course.lessons.count()
        
        # Calculate progress
        if total_lessons == 0:
            self.progress = 0
        else:
            self.progress = (completed_lessons / total_lessons) * 100
        
        # Save the progress and return it rounded
        self.save()
        return round(self.progress, 2)
    
    def calculate_average_grade(self):
        # Filter submitted assignment associated with the course and count them
        submitted_assignments = StudentAssignment.objects.filter(course=self.course, student=self.student, handed_in=True)
        amount = submitted_assignments.count()

        # Initialize sum
        total_grade = 0
        
        # Sum the grades of submitted assignments
        for assignment in submitted_assignments:
            if assignment.grade is not None:  # Ensure grade is not None
                total_grade += assignment.grade
        
        # Return the average or 0 if no graded assignments were found
        return round(total_grade / amount, 2) if amount > 0 else 0


    def get_last_accessed_lesson_order(self):
        # Get the last completed lesson, ordered by 'order'
        last_completed = self.completed_lessons.order_by('order').last()

        if last_completed:
            # Try to get the next lesson after the last completed one
            next_lesson = Lesson.objects.filter(course=self.course, order__gt=last_completed.order).order_by('order').first()
            
            if next_lesson:
                return next_lesson.order
            else:
                # All lessons completed, return the order of the last completed lesson
                return last_completed.order
        else:
            # If no lessons have been completed, return the first lesson of the course
            first_lesson = Lesson.objects.filter(course=self.course).order_by('order').first()
            return first_lesson.order if first_lesson else None
        

    def __str__(self):
        return f"{self.student} enrolled in {self.course}."
    

class LessonCompletion(models.Model):
    # Intermediary table that handles the relationship between Enrollment and Lesson models to store metadata about it
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_complete = models.BooleanField(default=False)

class StudentAssignment(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='assignments')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assignments")
    file = models.FileField(storage=MediaStorage(), upload_to='assignment_files/')
    handed_in = models.BooleanField(default=False)
    date_handed_in = models.DateTimeField(auto_now_add=True)
    grade = models.IntegerField(null=True, blank=True, validators=[MaxValueValidator(10), MinValueValidator(1)])

    def __str__(self):
        return f"Id: {self.id}, Grade: {self.grade}"



#----------- QUIZ RELATED MODELS ---------------#

class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    name = models.CharField(max_length=70)
    difficulty = models.CharField(max_length=10, choices=[('easy', 'Easy'),
                                                          ('medium', 'Medium'),
                                                          ('hard', 'Hard'),])
    number_of_questions = models.PositiveIntegerField()
    time = models.PositiveIntegerField() # Duration of the quiz in minutes
    required_score = models.IntegerField() # Required score to pass the quiz in %

    def __str__(self):
        return self.name
    
    def get_questions(self):
        return self.question_set.all()
    
    class Meta:
        verbose_name_plural = "Quizzes"

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    image = models.ImageField(upload_to='quiz_images/', blank=True, null=True)
    question_order = models.PositiveIntegerField()

    def __str__(self):
        return self.text


class Answer(models.Model):
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')

    def __str__(self):
        return self.text


class StudentQuizSession(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    correct_answer_count = models.IntegerField(default=0)
    passed = models.BooleanField(default=False)
    solved_in = models.PositiveIntegerField(default=0) # store in seconds

    def calculate_score(self):
        total_questions = self.quiz.questions.count()
        # Calculate score as a percentage
        score_percentage = (self.correct_answer_count / total_questions) * 100

        # Change the 'passed' flag if needed
        if score_percentage >= self.quiz.required_score:
            self.passed = True
            self.save()

        return round(score_percentage, 2)
    

    def __str__(self):
        student = self.student if self.student else "Unknown Student"
        quiz = self.quiz if self.quiz else "Unknown Quiz"
        return f"{student} - {quiz}"



class StudentAnswer(models.Model):
    session = models.ForeignKey(StudentQuizSession, on_delete=models.CASCADE, related_name="student_answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer =  models.CharField(max_length=200, blank=True, null=True, default=None)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return str(self.selected_answer) if self.selected_answer else "No answer selected"
    
class Notification(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="sent_notifications", null=True, blank=True) # Who triggered the notification
    recipient = models.ManyToManyField(Profile, related_name='notifications')  # Who the notification is for
    message = models.CharField(max_length=350, blank=True, null=True)
    is_read = models.BooleanField(default=False)  # To track if the notification has been read
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.message[:40]}"  # Return the first 40 characters of the message

    

