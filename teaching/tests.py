from django.urls import reverse
from users.models import *
from users.tests import BaseTestCase
from rest_framework.test import APITestCase
from rest_framework import status

class CourseViewTests(BaseTestCase):
    def setUp(self):
        self.client.login(username="instructor1", password="password123")
    
    def test_create_course_view_access(self):
        # Check if the instructor can access the create course page
        response = self.client.get(reverse("teaching:create_course"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "teaching/new_course.html")
    
    def test_course_edit_view_context(self):
        # Access the edit view and check the context data
        response = self.client.get(reverse("teaching:edit_course", kwargs={"pk": self.course1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "teaching/course_edit.html")
        self.assertEqual(response.context["course"], self.course1)

        # Ensure that two lessons, belonging to the course1, are in place
        self.assertContains(response, "Lesson 1")
        self.assertContains(response, "Lesson 2")
    


class APICourseViewSetTests(APITestCase, BaseTestCase):
    def setUp(self):
        self.client.login(username="instructor1", password="password123")

    def test_create_course_success_api(self):
        """Test creating a new course successfully."""
        url = '/teaching/api/courses/create_course/'
        data = {
            "title": "New Course",
            "description": "This is a new course.",
        }
        response = self.client.post(url, data, format='json')
    
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 3)  # Two pre-created and one new
        self.assertEqual(Course.objects.last().title, "New Course")
    
    
    def test_edit_and_save_course_changes_api(self):
        # Test updating a course through the custom API endpoint
        url = f"/teaching/api/courses/{self.course1.pk}/save_course_changes/"
        response = self.client.put(url, data={"title": "Updated Course"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course1.refresh_from_db()
        self.assertEqual(self.course1.title, "Updated Course")
    

class AddLessonViewTest(BaseTestCase):
    def setUp(self):
        self.client.login(username="instructor1", password="password123")

    def test_add_lesson_success(self):
        response = self.client.post(
                reverse('teaching:add_lesson', kwargs={"pk": self.course1.pk}),
                # The POST method expects the data to be submitted as a dictionary under the data parameter
                data={'title': 'Lesson 3', 'order': 3, 'content': 'test'},
                follow=True, # Without this line status_code would be 302 (a redirect), but for test we have to follow a redirect
        )

        self.assertEqual(response.status_code, 200)

        # Ensure redirect from 'Add lesson' page to 'Edit Course'(successful form submission)
        self.assertContains(response, 'Edit Course') 

        # Ensure newly added lesson on the page we got redirected to - is in the list
        self.assertContains(response, 'Lesson 3') 

    
    def test_add_lesson_fail(self):
        # Attempt to submit lesson form without specifying an order
        response = self.client.post(
                reverse('teaching:add_lesson', kwargs={"pk": self.course1.pk}),
                # The POST method expects the data to be submitted as a dictionary under the data parameter
                data={'title': 'Lesson 3', 'content': 'test'},
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Edit Course') # Ensure no redirect from 'Add lesson' page to 'Edit Course'


class EditLessonViewTest(BaseTestCase):
    def setUp(self):
        self.client.login(username="instructor1", password="password123")

    def test_edit_lesson(self):
        response = self.client.post(
                reverse('teaching:edit_lesson', kwargs={"pk": self.course1_lesson1.pk,}),
                # The POST method expects the data to be submitted as a dictionary under the data parameter
                data={'title': 'Lesson changed', 'order': 1, 'content': 'Test 1'},
                follow=True, # Without this line status_code would be 302 (a redirect), but for test we have to follow a redirect
        )

        self.assertEqual(response.status_code, 200)
        # Ensure redirect from 'Add lesson' page to 'Edit Course'(successful form submission)
        self.assertContains(response, 'Edit Course') 

        # Ensure both lessons appear - one changed and one not
        self.assertContains(response, 'Lesson changed') # Previously "Lesson 1"
        self.assertContains(response, 'Lesson 2') # Remained unchanged
        
