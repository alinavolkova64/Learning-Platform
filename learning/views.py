from django.shortcuts import render, redirect
from users.models import *
from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from users.utils import send_notification
from django.utils.timezone import now
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
from django.urls import reverse_lazy

#-----------------------------------------------------------
# Mixins
#-----------------------------------------------------------
class RoleRequiredMixin(LoginRequiredMixin):
    """
    Is used to check the required role of the user 
    and redirect unauthorized user to the login page.
    """
    required_role = None  # Specify the required role later in the view
    login_url = reverse_lazy('login') # Redirect unauthorized user to login page
    
    def dispatch(self, request, *args, **kwargs):
        # ensure the user is authenticated (LoginRequiredMixin handles this)
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)  # This will redirect to the login page

        # Then check the user's role
        if not self.has_required_role():
            return HttpResponseForbidden("You don't have the required role to access this page.")
        
        return super().dispatch(request, *args, **kwargs)

    # def has_required_role(self):
    #     return self.request.user.profile.role == self.required_role

    def has_required_role(self):
    # Ensure the user's profile and role attribute exist
        return getattr(self.request.user.profile, 'role', None) == self.required_role


class StudentEnrollmentMixin:
    def get_enrolled_courses(self):
        student_profile = self.request.user.profile
        # Using select_related() to reduce the amount of database queries
        return Enrollment.objects.filter(student=student_profile).select_related('course')
    

#-----------------------------------------------------------
# Student-related views
#-----------------------------------------------------------

class StudentDashboardView(RoleRequiredMixin, StudentEnrollmentMixin, TemplateView):
    """
    Handles the student's dashboard view, providing course progress.

    GET: Displays the dashboard for students, showing an overview of their 
    enrolled courses, progress, and relevant data. This view extends `TemplateView` 
    and enforces role-based access control using mixins.

    POST: (For testing purposes) Demonstrates how `WebSocket.onmessage` can trigger 
    live notification updates for the current user without requiring a page reload.
    """
    template_name = 'learning/student_dashboard.html'
    required_role = 'student'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrolled_courses = self.get_enrolled_courses()
        student = self.request.user.profile
        
        context["course_progress_data"] = [
            {
                'course': enrollment.course.title,
                'progress': enrollment.calculate_progress(),
                'last_accessed_lesson_order': enrollment.get_last_accessed_lesson_order(),
                'last_accessed_lesson': Lesson.objects.get(course=enrollment.course,
                                                           order=enrollment.get_last_accessed_lesson_order()),
                'completed_assignments': StudentAssignment.objects.filter(course=enrollment.course, student=student, 
                                                                          handed_in=True).order_by('-date_handed_in'),
                'average_grade': enrollment.calculate_average_grade(),
            }
            for enrollment in enrolled_courses
        ]
        return context
    

    def post(self, request, *args, **kwargs):
        # Create a test notification for current user
        notification = Notification.objects.create(
            sender=None,
            message=f"Notification is test",
        )
        # Add the current user's profile as the recipient
        notification.recipient.add(self.request.user.profile)
        notification.save()
        send_notification(notification) # Call for helper function
        
        # Return a JSON response indicating success
        return JsonResponse({'status': 'success', 'message': 'Notification created successfully.'})


class Notifications(View):
    """
    Returns the latest notifications in JSON format for the 
    StudentDashboardView to allow real-time updates via JavaScript.
    """
    def get(self, request, *args, **kwargs):
        # Get the notifications for the current user
        student = request.user.profile
        notifications = Notification.objects.filter(recipient=student).order_by('-timestamp')

        # Serialize the notifications to send as JSON
        notifications_data = [
            {
                'message': notif.message,
                'timestamp': notif.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for notif in notifications
        ]

        return JsonResponse({
            'notifications': notifications_data,
        })


class NewNotifCount(RoleRequiredMixin, View):
    """
    Returns the count of unread notifications for the current user 
    in JSON format to support real-time updates in the UI.
    """
    required_role = 'student'

    def get(self, request, *args, **kwargs):
        student = self.request.user.profile

        # Get the count of new notifications for the current student
        count = Notification.objects.filter(recipient=student, is_read=False).count()
        
        return JsonResponse({'new_notifications_count': count})
    

class MarkNotificationsRead(View):
    """
    Marks all unread notifications as read for the current user.
    """
    def put(self, request, *args, **kwargs):
        student = self.request.user.profile
        # Update all unread notifications for the current student
        Notification.objects.filter(recipient=student, is_read=False).update(is_read=True)

        return JsonResponse({'success': 'True'})
    

class LessonView(RoleRequiredMixin, TemplateView):
    """
    View for rendering a specific lesson within a course for students,
    allows students to engage with course materials(watch video, read and download lesson contents) 
    and submit their assignments.

    Methods:
        - post: Handles the submission of assignments by students.
            Upon receiving an assignment file, it creates a StudentAssignment record,
            marks the lesson as complete in the LessonCompletion model, and redirects
            the user back to the lesson page.
            If no file is submitted, it redirects the user back to the lesson page without
            making changes.
    """
    template_name = 'learning/lesson.html'
    required_role = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Access the URL parameters from kwargs
        course_title = self.kwargs['course_title']
        lesson_order = self.kwargs['lesson_order']

        # Get the course and lesson based on the URL parameters
        course = get_object_or_404(Course, title=course_title)
        lesson = get_object_or_404(Lesson, order=lesson_order, course=course)
        student = self.request.user.profile

        # Query for previous and next lessons
        previous_lesson = Lesson.objects.filter(course=course, order=lesson.order - 1).first()
        next_lesson = Lesson.objects.filter(course=course, order=lesson.order + 1).first()

        # Add the course and lesson to the context
        context['course'] = course
        context['lesson'] = {
            'title': lesson.title,
            'order': lesson.order,
            'is_complete': LessonCompletion.objects.filter(enrollment__student=student, lesson=lesson, 
                                                           is_complete=True).exists(),
            'content': lesson.content,
            'video_file': lesson.video_file,
            'video_url': lesson.video_url,
            'homework_requirements': lesson.homework_requirements,
            'pdf': lesson.pdf,
            'previous_lesson_order': previous_lesson.order if previous_lesson else None,
            'next_lesson_order': next_lesson.order if next_lesson else None,
        }
        context['quizzes'] = Quiz.objects.filter(lesson=lesson)
        return context
    

    def post(self, request, course_title, lesson_order):
        # Handling the submission of assignments by students
        course = get_object_or_404(Course, title=course_title)
        lesson = get_object_or_404(Lesson, order=lesson_order, course=course)
        student = request.user.profile
        enrollment = get_object_or_404(Enrollment, student=student, course=course)

        # Check if an assignment file is included in the request
        if 'assignment' in request.FILES:
            assignment_file = request.FILES['assignment']

            # Validate the file type
            if not assignment_file.name.endswith('.pdf'):
                return HttpResponse("Invalid file type. Please upload a PDF file.", status=400)

            # Create and save the StudentAssignment object
            StudentAssignment.objects.create(student=student, lesson=lesson, course=course,
                                            file=assignment_file, handed_in=True)

            # Update completion status in LessonCompletion model
            LessonCompletion.objects.update_or_create(enrollment=enrollment, lesson=lesson,
                                                        defaults={'is_complete': True})

            return redirect('learning:lesson', course_title=course.title, lesson_order=lesson.order)
        
        # Handle case where no file is submitted
        return redirect('learning:lesson', course_title=course.title, lesson_order=lesson.order)



#-----------------------------------------------------------
# Quiz-related views
#-----------------------------------------------------------
class QuizListView(ListView, RoleRequiredMixin, StudentEnrollmentMixin):
    """
    View for displaying available quizzes list belonging to the courses a student is enrolled in.
    """
    model = Quiz
    template_name = 'learning/quizzes.html'
    required_role = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrolled_courses = self.get_enrolled_courses()

        context['quizzes'] = [
            {
                'course_name': enrollment.course.title,
                'quizzes': [
                    {
                        'quiz': quiz,
                        'session': StudentQuizSession.objects.filter(
                            student=self.request.user.profile,
                            quiz=quiz
                        ).first()  # Retrieve the session if it exists
                    }
                    for quiz in enrollment.course.quizzes.all()
                ]
            }
            for enrollment in enrolled_courses
        ]

        return context
    

class QuizStartView(TemplateView, RoleRequiredMixin):
    """
    View for displaying the start page of the quiz with its details (if the quiz was yet not completed), 
    then creates new QuizSession instance.
    Else displays student's score.
    """
    template_name = 'learning/quiz_start.html'
    required_role = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz_id = self.kwargs['quiz_id']
        # Get the quiz based on the URL parameters
        quiz = get_object_or_404(Quiz, id=quiz_id)

        # Clear any previous quiz session data
        self.request.session.pop('quiz_start_time', None)
        self.request.session.pop('quiz_status', None)
        self.request.session.pop('quiz_time_limit', None)

        session_exists = False
        session = StudentQuizSession.objects.filter(student=self.request.user.profile, quiz=quiz, completed=True).first()

        # Create a student quiz session, if no such was previously created and completed
        if not session:
            session = StudentQuizSession.objects.create(student=self.request.user.profile, quiz=quiz)   
        else:
            session_exists = True
            
        # Add quiz details to the context
        context['quiz'] = quiz
        context['session'] = session
        context['session_exists'] = session_exists
        return context
    
        
class QuizQuestionView(TemplateView, RoleRequiredMixin):
    """
    GET: Displays question of the quiz with answer options, shows the percentage of quiz questions completed, starts the timer.
    POST: Retrieves student's selected answer, saves it to the database with 'is_correct' flag.
        - If student returns to the previous question's page - deletes previous StudentAnswer
            instance from the database and creates a new record.
        - If quiz is out of questions, student is redirected to quiz completion page with calculated results.
    """
    template_name = 'learning/quiz_question.html'
    required_role = 'student'

    def get(self, request, quiz_id, question_order, *args, **kwargs):
        quiz = get_object_or_404(Quiz, id=quiz_id)

        # Check if the timer is already started
        if 'quiz_start_time' not in request.session:
            request.session['quiz_start_time'] = now().isoformat() # Initialize the timer
            # Set the time limit using quiz duration (in min) set by instructor
            request.session['quiz_time_limit'] = quiz.time * 60 

        # Retrieve the timer info
        quiz_start_time = request.session.get('quiz_start_time')
        time_limit = request.session.get('quiz_time_limit')

        # Calculate elapsed time
        quiz_start_time = now().fromisoformat(quiz_start_time)
        elapsed_time = (now() - quiz_start_time).total_seconds()

        # Check if the timer has run out
        if elapsed_time > time_limit:
            return redirect('learning:quiz_complete', quiz_id=quiz_id) 

        # Calculate remaining time
        remaining_time = int(time_limit - elapsed_time)

        #---------------------------------------

        # Retrieve the session
        session = StudentQuizSession.objects.filter(student=request.user.profile, quiz=quiz).first()

        # Determine the question to display based on the current question order
        question = Question.objects.filter(quiz=quiz).order_by('question_order')[question_order - 1]

        total_questions = quiz.questions.count() 
        progress_percentage = ((question_order -1) / total_questions) * 100

        context = {
            'quiz': quiz,
            'question': question,
            'question_order': question_order,
            'total_questions': total_questions,
            'progress_percentage': round(progress_percentage, 2),
            'session': session,
            'remaining_time': remaining_time,
        }
        
        return render(request, self.template_name, context)
    

    def post(self, request, quiz_id, question_order, *args, **kwargs):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        session = StudentQuizSession.objects.filter(student=request.user.profile, quiz=quiz).first()
        question = get_object_or_404(Question, quiz=quiz, question_order=question_order)

        selected_answer_id = request.POST.get('student_answer') # Get student's selected answer
        # Retrieve Answer object that student selected, based on answer's id
        try:
            selected_answer = Answer.objects.get(id=selected_answer_id)
        except Answer.DoesNotExist:
            selected_answer = "No answer selected"  # Handle invalid ID or no answer selected case

        # Use related name to filter correct answers to this question
        correct_answer = question.options.filter(is_correct=True).first()
        is_correct = selected_answer == correct_answer

        # Check if an answer for this question already exists and delete it
        StudentAnswer.objects.filter(session=session, question=question).delete()

        # Save the student's answer to the database
        StudentAnswer.objects.create(
            session=session,
            question=question,
            selected_answer=selected_answer,
            is_correct=is_correct,
        )

        next_question_order = question_order + 1
        # Handle quiz completion if out of questions
        if next_question_order > Question.objects.filter(quiz=quiz).count():
            session.completed = True
            session.correct_answer_count = StudentAnswer.objects.filter(is_correct=True, session=session).count()
            session.score = session.calculate_score()


            # Convert the start time from the session (which is a string) to a datetime object
            quiz_start_time_str = request.session.get('quiz_start_time')
            if quiz_start_time_str:
                quiz_start_time = datetime.fromisoformat(quiz_start_time_str)
                # Calculate the time difference and save it in 'solved_in'
                session.solved_in = (now() - quiz_start_time).total_seconds()

            session.save()
            return redirect('learning:quiz_complete', quiz_id=quiz_id) 
        
        # Else get the next question 
        return redirect('learning:quiz_question', quiz_id=quiz.id, question_order=next_question_order)
    


class FinalizeQuizView(View):
    """
    Works as a fallback mechanism for when the timer runs out. 
    View ensures that, even if the user doesn’t manually submit their final answer due to the timer expiring, 
    the quiz session is finalized on the backend.
    """
    def post(self, request, quiz_id, *args, **kwargs):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        session = StudentQuizSession.objects.filter(student=request.user.profile, quiz=quiz).first()
        
        if not session:
            return JsonResponse({"success": False, "message": "Session not found."})
        
        if not session.completed:
            session.completed = True
            session.correct_answer_count = StudentAnswer.objects.filter(is_correct=True, session=session).count()
            session.score = session.calculate_score()
            session.solved_in = quiz.time * 60
            session.save()

        return JsonResponse({"success": True})

    


class QuizCompleteView(TemplateView, RoleRequiredMixin):
    """
    Displays student's quiz session's score, as well as the table with submitted vs correct answers
    """
    template_name = 'learning/quiz_complete.html'
    required_role = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz_id = self.kwargs['quiz_id']
        quiz = get_object_or_404(Quiz, id=quiz_id)
        session = StudentQuizSession.objects.filter(student=self.request.user.profile, quiz=quiz).first()
        # Calculate the minutes and seconds in the view
        session_minutes = int(session.solved_in // 60)
        session_seconds = int(session.solved_in % 60)

        # Clear quiz-related session data
        self.request.session.pop('quiz_start_time', None)
        self.request.session.pop('quiz_status', None)
        self.request.session.pop('quiz_time_limit', None)
        
        context['quiz'] = quiz
        context['session'] = session
        context['submitted_answers'] = StudentAnswer.objects.filter(session=session)
        context['session_minutes'] = session_minutes
        context['session_seconds'] = session_seconds
        return context
        