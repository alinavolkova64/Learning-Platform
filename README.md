# Online learning platform 
#### Final project made by Alina Volkova for CS50Web Course

---


## Table of Contents
1. [Project Description](#project-description)
    * [Why This Project?](#why-this-project)
    * [Overall Project Goals](#overall-project-goals)

2. [Distinctiveness and Complexity](#distinctiveness-and-complexity)
    * [Distinctiveness](#distinctiveness)
    * [Complexity](#complexity)

3. [Contents of each file](#contents-of-each-file)
    * [Users app](#users-app)
    * [Learning app](#learning-app)
    * [Teaching app](#teaching-app)
    * [Project Root - capstone](#project-root---capstone)

4. [Overview of Project Features](#overview-of-project-features)

5. [How to Run the Application](#how-to-run-the-application)
    * [Installation Instructions](#installation-instructions)
    * [Demo Accounts](#demo-accounts)
    * [Usage](#usage)

6. [Additional Information for Staff](#additional-information-for-staff)
    * [Explanation of Key Code Design Decisions](#explanation-of-key-code-design-decisions)

---

## Project Description
**Online Learning Platform:** This project is a fully-functional online learning platform designed to empower users to learn and teach with ease. 
The platform allows students to register, explore and enroll in a variety of courses, watch lecture videos, complete assignments, take interactive quizzes and track their progress. 
Instructors can create and manage courses and lessons, upload lesson content, track students' progress, view and grade submitted assignments.

This platform is designed to offer an intuitive and engaging learning experience by combing modern technologies with the flexibility of online education.

#### Why This Project?
The idea for this project stems from my admiration for online learning platforms. They have allowed me to learn programming independently and structure my education in a way that feels meaningful and satisfying. Without such platforms, I would likely have pursued a more traditional path. While that's not inherently bad, I appreciate the freedom and accessibility online education offers. This project is my way of showcasing how such platforms can empower individuals like me.

#### Overall Project Goals
This project intentionally prioritizes adaptability over standardization. By mixing tools and approaches, I aimed to demonstrate my understanding of Django’s core functionalities and beyond. While I recognize the importance of consistency in production, **I used this project as an opportunity to expand my skill set in the first place**, as well as to showcase my ability to adapt to different paradigms and requirements.

---
## Distinctiveness and Complexity
### Distinctiveness
This project stands out from the previous ones in several ways, both **in scope and feature set**. Unlike the auction-based e-commerce platform or the blog-style social network, this application is an online learning platform designed to provide **dynamic, role-specific functionality**, and a focus on coherent education and user experience. The differences are outlined below:
&nbsp;
1. **Role-Based Functionality:** Unlike previous projects, which featured a single user role (e.g. buyer, poster), this project has two distinct user roles — *students and instructors* — each with tailored functionality and dashboards.
    &nbsp;&nbsp;&nbsp;&nbsp; - **Students:** Track course progress, watch lectures, participate in interactive quizzes, and access a personalized dashboard showing grades, assignments, and last accessed lessons (students can resume lessons from where they left off) - features not present in previous projects.
    &nbsp;&nbsp;&nbsp;&nbsp;- **Instructors:** Manage courses and their lessons, upload content (videos, PDFs, images), create, view and grade assignments, share live announcements and monitor student performance via instructor's dashboard - database management features, that also were not seen in previous projects.
    &nbsp;
2. **Real-Time Features:** The platform integrates <ins>WebSocket technology via Django Channels</ins> for real-time notifications, not seen in previous projects. This **live-update system** allows instructors to send urgent or important announcements to students, enhancing communication without introducing unnecessary social network-like functionality.
&nbsp;
3. **Quizzes with Enhanced User Experience:**
    * One-question-per-card design.
    * Real-time feedback(answer comparison, results) after each quiz submission.
    * Timer functionality.
    * Progress bar.

    This unique feature is intended for the educational, <ins>interactive</ins> environment that will allow more interesting learning-in **contrast to purely social media-like features or trivial ecommerce transactions**.
&nbsp;
4. **Multiple Apps:** While prior projects focused on simpler Django implementations, this project leverages multiple apps(3) for modularity, adhering to a modular architecture to separate concerns (e.g., user authentication, instructor's and student's role-based functionality). This structure enhances maintainability and scalability.
&nbsp;
5. **File Management:** Instructors can upload and manage a variety of file types, including images, videos, and PDFs, which required implementing logic for secure handling, storage, and rendering across different pages. <ins>This capability was not present in prior projects</ins>, which were limited to simple text or images.
&nbsp;
6. **Custom Design:** The project avoids using frameworks like Bootstrap and instead employs custom CSS with media queries for a more **personalized and mobile-responsive design**.
&nbsp;
### Complexity
This project demonstrates technical depth in several areas:

1. Usage of **Django REST Framework** for efficient data handling on the instructor's dashboard.
&nbsp;
2. **Class-Based Views (CBVs):** Utilized throughout the project for modular, reusable, and maintainable code. CBVs, being more advanced than function-based views, allow the use of mixins and other modular patterns.
&nbsp;
3. Real-time updates implemented via **WebSockets and Django Channels**, a technology not taught in the course but crucial for delivering live notifications. Most of the e-learning systems provide chats or discussion boards. In contrast, this project proposes specifically a notification system. Notifications are **immediate** and relevant, offering a way to share urgent or important information between instructors and students. <ins>This feature was designed to add meaningful functionality to the platform, while adhering to project constraints against creating a social network-like messaging system.</ins>  
&nbsp;
4. **Frontend Interactivity:**
    * Extensive use of JavaScript and AJAX enables seamless and interactive user experiences, including editing course data without page reloads, dynamically updating timers, filtering assignments, and integrating API responses. 
    Features such as toggling detailed views (e.g., quiz results' answer tables or FAQ answers appear on button click) and displaying additional information only when needed - **ensure the interface remains clean and user-friendly**, avoiding overwhelming users with excessive data.
    * **Custom** responsive design using CSS and media queries.
&nbsp;
5. **Database Design:**
The database schema is structured to accommodate the platform's complex features and maintain clarity in relationships:
    * A total of **15 models** ensure the application avoids overloading individual models and instead organizes data into logical relationships for improved maintainability and clarity.
    * A **through-model** (LessonCompletion) is used to store metadata about completed lessons, separating this data from the Lesson model itself to maintain focus and relevance.
    * Many-to-many relationships, such as courses linked to multiple fields of study, allow for **efficient filtering** and searching without data redundancy.
    * Some models include **custom methods** to handle repetitive actions specific to their role, such as calculating course progress or average grades, minimizing redundancy in the codebase and improving functionality.
    * The separation of user roles into students and instructors ensures distinct functionality for each, while still utilizing a shared authentication system for simplicity and coherence.
&nbsp;
6. **Enhanced User Experience:** Features like the ability to return to the last accessed lesson, to edit course information inline, to see quiz progress dynamically (progress bar) or a timer that updates every second no matter what page the user is on, the ability to view PDF files without needing to download them or reload the page (using a PDF.js library) - all add a layer of personalization and usability to the platform, requiring thoughtful backend logic and frontend design.

#### These additions demonstrate my willingness to go beyond the course material and learn new concepts to create a more versatile project.
---
## Contents of each file
To maintain clarity, the files are grouped based on their respective apps: users, learning, and teaching. The descriptions provide an overview of the purpose and functionality of each file, highlighting their roles within the project.
### Users App
**This app is responsible for general-purpose functionality, including user authentication, anonymous browsing, viewing and enrolling in courses. It also manages shared models used across the project and the WebSocket configuration.**

• `models.py`: Contains all project models, including user profiles, courses, lessons, assignments, quizzes, and related metadata. The decision to centralize models here ensures consistency and simplifies inter-app data relationships.
• `views.py`: Handles user authentication (login, logout, and registration), viewing/filtering courses, and enrollment logic.
• `urls.py`: Maps URLs for general site navigation and user account actions.
• `admin.py`: Configures Django’s admin interface for managing all project's models.
• `forms.py`: Contains forms such as CourseFilter for filtering course listings and RegistrationForm for user registration.
• `tests.py`: Contains test cases for user-related functionality, such as authentication, course filtering and enrollment.

**WebSocket-related files**
• `apps.py`: Loads and registers signal handlers during app initialization to handle tasks like notifications or data updates.
• `consumers.py`: Consumers manage the lifecycle of a WebSocket connection, handling the WebSocket events like connect, receive, disconnect and notify(custom event for processing messages and broadcasting them to the client).
• `routing.py`: This file works like `urls.py`, but instead of routing HTTP requests, it routes WebSocket connections to consumers.
• `signals.py`: Defines Django signal handler for sending notifications when Notification model is saved.
• `utils.py`: Includes helper function, that explicitly invokes the notify method in `consumers.py`.


&nbsp;
#### templates/users/:
○ `layout.html`: Base template extended by other templates across apps for consistent site structure.
○ `login.html`, `register.html`: Templates for user authentication pages.
○ `homepage.html`: The landing page for both authenticated and anonymous users.
○ `courses.html`: Page listing all available courses with filtering options by level and/or field of study.
○ `course_details.html`: Displays detailed information about a specific course, including its description, lesson titles, and reviews.

#### static/:
○ `styles.css`: Main CSS file for styling the general site layout.
&nbsp;

### Learning App
**This app manages functionality and features available to students after enrolling in at least one course.**

• `views.py`: Handles logic for student dashboards, lessons, quizzes, assignments, and progress tracking.
• `urls.py`: Defines routes for accessing the student dashboard, lessons, assignments, and quizzes.
• `tests.py`: Includes tests for the main features of the application, such as submitting assigment for lesson, accessing student dashboard before/after altering the database, and tests for the entire quiz workflow:
&nbsp;&nbsp;&nbsp;&nbsp;- Quiz initialization (starting a quiz).
&nbsp;&nbsp;&nbsp;&nbsp;- Quiz question submission (answering individual questions).
&nbsp;&nbsp;&nbsp;&nbsp;- Quiz result page (viewing the final score and completion status).

#### templates/learning/:
○ `student_dashboard.html`: Displays the student's progress, grades, assignments, and latest notifications.
○ `lesson.html`: Renders video lectures, PDFs, quizzes, assignment submission forms, and navigation between lessons.
○ `quizzes.html`: Displays a list of all quizzes available in enrolled courses, with results for completed quizzes.
○ `quiz_start.html`: Provides general information (e.g., timer settings, topic) about a specific quiz before it begins.
○ `quiz_question.html`: Displays quiz questions with answer options, a dynamically updated timer, a progress bar, and optional image rendering.
○ `quiz_complete.html`: Shows results of the just-completed quiz, including pass/fail status, time taken, score, and a table comparing submitted and correct answers.
#### static/learning/:
○ `main.js`: The primary JavaScript file, responsible for managing timers, WebSocket connections, dynamic UI elements, and filters.
○ `learning_styles.css`: Styles student-related pages and elements, like the dashboard and quizzes.
&nbsp;
### Teaching App
**This app provides instructors with tools to manage courses, lessons, view/grade assignments and interact with students.**

• `views.py`: Handles instructor-specific functionality, including creating and updating courses and lessons, and posting announcements.
• `urls.py`: Defines routes for accessing API endpoints, the instructor dashboard, and managing course content.
• `forms.py`: Includes forms for creating and updating courses and lessons, such as CourseForm and LessonForm.
• `serializers.py`: Contains serializers for models like Course, Lesson, and StudentAssignment, enabling data transformation for API endpoints.
• `tests.py`: Includes test cases for instructor-specific actions like creating and editing courses, adding and changing lesson data, testing API endpoints.
#### templates/teaching/:
○ `instructor_dashboard.html`: Displays course statistics and provides options for managing courses, viewing and/or grading assignments, and sending announcements.
○ `new_lesson.html`: Form template for creating a new lesson.
○ `new_course.html`: Form template for creating a new course.
○ `lesson_edit.html`: Form template for detailed editing of existing lessons.
○ `course_edit.html`: Form template for dynamically editing existing courses, lists lessons of the course with editing/deleting options.
○ `confirm_delete.html`: Confirmation page for deleting courses or lessons.
#### static/teaching/:
○ `api_related.js`: Handles API calls for managing course data and dynamic announcement submission.
○ `teaching_styles.css`: Styles instructor-related pages, such as the dashboard and forms.
&nbsp;
### Project Root - `capstone`
**Shared files and configurations used across the entire project for consistency and setup:**

• `settings.py`: Contains Django configuration, including static file setup, media files setup, Channel layer setup, database connections, app registrations, and middleware.
• `urls.py`: Maps root-level URLs to app-level URL configurations for users, learning, and teaching.
• `asgi.py`: Configures ASGI application settings for handling both asynchronous WebSocket connections and synchronous HTTP requests, which serves as an entry point for Django Channels.
• `routing.py`: This file routes WebSocket connections to the appropriate app-level routing. It's essentially the bridge between the ASGI application and the app's WebSocket routing.
• `media` folder:  automatically created to store user-uploaded content for the project. It is structured to organize various types of uploaded files related to lessons, quizzes, and assignments:

- lesson_videos/: Stores video files associated with individual lessons.
lesson_pdfs/: Contains PDF files uploaded as lesson resources or additional materials.

- assignment_files/: Used for storing files submitted by students as part of their assignments.
- quiz_images/: Holds images uploaded for use in quiz questions.

This folder is located at the project level to ensure all apps can share the same media storage location. It plays a critical role in handling the diverse content types required for the learning platform.

---
## Overview of Project Features
**Home Page Contents:**
    ○ Introduction to the platform, testimonials, and FAQs.
    ○ Sign-up and log-in buttons.
    ○ Call-to-action (CTA) buttons for browsing courses.
    ○ Contact form for support requests.
    ○ General information (contact details, social media links, etc.).

**User Authentication Pages**
    • **Sign-Up Page:**
        ○ User registration form (name, email, password, role selection: student or instructor).

• **Login Page:**
        ○ Username and password input fields.
&nbsp;
**Course Listing Page:**
    • Displays all available courses with filtering options (by category and/or level).
    • Course cards include a short description and the instructor's name.

**Course Detail Page:**
    • Includes the course title, description, syllabus, instructor bio, user reviews, and prerequisites (if any).
    • Enrollment button (redirects to the first lesson).
    • Displays a progress bar for students already enrolled in the course.

### **Dashboard (Separate for Students and Instructors):**
**Student Dashboard:**
        ○ Lists enrolled courses with links to the last accessed lesson.
        ○ Tracks course progress (percentage completed).
        ○ Displays assignments (filter by pending/submitted and see grading status).
        ○ Shows average grades for enrolled courses.
        ○ Includes a notification section with live updates via WebSocket. Features a visual indicator (a bell icon) that shows the number of unread notifications. Clicking the icon opens a dropdown with the notifications and resets the unread count to zero(includes a test button for real-time notifications).

**Instructor Dashboard:**
        ○ Course management panel (create, view, edit, or delete courses and lessons; some materials edited via REST API framework).
        ○ Enrollment statistics.
        ○ Assignments management (filter student submissions by course and grading status, view PDFs on-page, and enter grades dynamically without reloading).
        ○ Announcement system (send live messages to specific courses or all students via WebSocket).

**Lesson Page:**
        ○ Embedded video player for lectures.
        ○ Downloadable resources (e.g., PDFs) and homework requirements.
        ○ Submission form for PDF assignments.
        ○ Quick access to lesson's associated quizzes (if any).
        ○ Lesson completion indicator updates status and marks lessons complete upon assignment submission.
        ○ Quick links to navigate between previous and next lessons.

### **Quiz Pages**
**Quiz Listing Page:**
        ○ Lists quizzes associated with courses a student is enrolled in, displaying solved ones with progress indicators.
        
**Quiz Start Page:**
        ○ Displays quiz information (topic, difficulty, related lesson and course, timer details).
        ○ Prevents retaking if already completed, showing previous results instead.

**Quiz Question Page:**
        ○ Supports single-choice and true/false questions, along with image rendering (if included).
        ○ Allows navigation back to previous questions (updates saved answers).
        ○ Timer updates in real-time for better UX.
        ○ Redirects to the completion page if time runs out, calculating scores based on submitted answers.

**Quiz Result Page:**
        ○ Instant feedback after submission (pass/fail status, percentage score, and an answer comparison table).


---
## How to Run the Application

### Installation instructions

To get this project running on your local machine, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/alinavolkova64/web50
    ```

2. Navigate to the project folder:
    ```bash
    cd web50\projects\2020\x\capstone
    ```

3. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use 'venv\Scripts\activate'
    ```

4. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

5. Run the development server:
    ```bash
    python manage.py runserver
    ```

6. Now, open your browser and go to `http://127.0.0.1:8000/` to view the application.
&nbsp;
7. Close the server after application use by `Ctrl + C`
&nbsp;
8. Run the tests (optional):
    ```bash
    python manage.py test 
    ```
&nbsp;
### Demo Accounts
For more realistic demonstration, the application comes preloaded with sample data to display its functionality, so rathen than spending time setting up users, courses and lessons, testers can focus on evaluating application's features and functionality without extra effort.

<ins>Below are the login credentials for two roles:</ins>
**Instructor Account**
    • Username: alice_white
    • Password: 12345qwerty
**Student Account**
    • Username: student_demo
    • Password: 12345qwerty
&nbsp;
### Usage
1. Visit the application's login page (link present in the navigation bar).
2. Enter the credentials above for either the instructor or student account.
3. Explore the corresponding dashboards and features:
    ○ **Instructor:** Create and manage courses, upload lessons, view/grade assignments, send announcements and monitor student progress.
    
    ○ **Student:** Access courses, complete lessons, take quizzes, view progress reports and test receiving notifications live (testing button included in the notifications section at /learning/student_dashboard/ , to see that WebSocket in particular is sending the notification: in your browser open 
    `Developer Tools -> Console -> Then press 'Create Test Notification' `
    on the dashboard to inspect the implementation of `notify` consumer method in action).
    
#### Notes
* No admin credentials. The application is designed to be explored using the demo accounts only.
* Any changes made during testing (e.g., adding courses, solving quizzes, submitting/grading assignments) will only affect tester's local database.
---

## Additional Information for Staff
### Explanation of Key Code Design Decisions 
1. **Centralized Models Decision:**
I decided to keep all the models in a single `models.py` file because they are so tightly connected and equally used across all apps. Splitting them into separate files or apps would have added **unnecessary complexity without offering real benefits**. Centralizing them keeps things simple and consistent.
&nbsp;
2. **Models Structure:**
I separated the User model into User and Profile to keep concerns organized:
    * The User model handles core authentication details (e.g., username, email, password).
    * The Profile model manages user-specific data (e.g., roles, bios), allowing flexibility for role-based permissions and other extensions.
&nbsp;
3. **Why Fewer Test Classes?**
&nbsp;
While there are multiple views in the `learning` app, the test methods are designed to verify the functionality of these views as **part of entire feature workflows**, rather than testing each view in isolation and introduce more redundancy.
    This approach implies that if the test results are correct - all connected views are already working coherently and fulfilling their purposes.
    ##### This ensures the application's key workflows are robust and reliable without unnecessary duplication of tests.

    **Tests Not Included**
    The tests do not cover asynchronous tasks or features dependent on JavaScript, such as real-time updates via WebSockets. Testing front-end behavior (DOM changes, UI/UX togglers, inline editing and dynamic form submission etc.) would require integration testing tools like Selenium or Cypress, that can simulate user interactions, but that's separate from Django's testing framework, that I am focusing on.

    In summary, the `tests.py` file prioritizes validating the critical relationships between views and the seamless functionality of features on the back-end.
&nbsp;
&nbsp;
4. **View Implementation Choices:**
* **Balancing Server-Rendered Views and APIs:**
I chose a mixed approach to showcase different paradigms:
    * Server-rendered views are used for features like file uploads and forms (e.g., lesson creation and editing), where simplicity and reliability are key.
    * DRF APIs power dynamic, interactive features like inline course detail editing.

    This dual approach highlights my ability to work with both modern and traditional patterns based on feature requirements.
&nbsp;    
* **Trade-offs Between Design and Learning Goals (Mixing FBVs, CBVs, and DRF):**
While I understand that real-world projects often emphasize consistency, I prioritized demonstrating a variety of skills. For instance:
    * **Function-Based Views (FBVs)** were used in 'users' app to demonstrate a clear understanding of how to implement logic directly without abstractions. These views showcase my grasp of the fundamentals.
    * **Class-Based Views (CBVs)** were used to showcase how I leverage Django’s abstractions for cleaner, <ins>reusable code</ins> (e.g.,  **the use of Django's generic views and mixins** (both built-in and custom ones), that helped with role-checking, template and form rendering etc.).
    * **Django Rest Framework (DRF)** API endpoints were used to highlight my ability to design modular, reusable backends (that are often required for scaling application to a mobile version), as well as the ability to work with serializers, custom actions, and DRF's request/response cycle. For example, course-management-related APIs (CourseViewSet) integrate serializers and custom actions effectively.

Some features use server-rendered views (e.g., lessons editing by instructors), while others leverage APIs (e.g., courses editing by instructors), **intentionally** illustrating flexibility and adaptability to project requirements. 
#### In production, I would focus on a single paradigm for scalability and maintainability of the code, but this project focuses on breadth and growth of the skill set, rather than uniformity.
