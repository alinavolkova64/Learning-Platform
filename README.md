# Online learning platform 
#### made by Alina Volkova, 2025

---
## Table of Contents
1. [About the Project](#about-the-project)
    * [Why This Project?](#why-this-project)
    * [Project Goals & Technical Focus](#project-goals--technical-focus)

2. [Tech Stack & Architecture](#tech-stack--architecture)
    * [Tech Stack](#️-tech-stack)
    * [Architectural Design](#️-architectural-design)

3. [Key Features](#key-features)
---

## About the Project
This fully-functional online learning platform allows students to enroll in courses, watch lecture videos, complete assignments, and take interactive quizzes—all while tracking their progress. Instructors can create and manage courses, upload lesson content, evaluate student submissions, and monitor overall engagement.

Designed for flexibility and ease of use, this platform combines modern web technologies to provide a seamless learning experience for both students and educators.

#### Why This Project?
As a self-taught developer, online learning platforms have played a crucial role in my education—allowing me to structure my learning and explore programming beyond traditional pathways. This project is both a tribute to the power of online education and a way to demonstrate my ability to design and implement scalable, interactive web applications.

#### Project Goals & Technical Focus
This project was built with Django and RESTful API principles, focusing on:
&nbsp;&nbsp;&nbsp;&nbsp;✔ Scalability & Modularity – Clean architecture for future expansion
&nbsp;&nbsp;&nbsp;&nbsp;✔ User-Centric Design – Intuitive navigation and responsive UI
&nbsp;&nbsp;&nbsp;&nbsp;✔ Practical Full-Stack Implementation – Backend logic and frontend interaction

---
## Tech Stack & Architecture  

### ⚙️ Tech Stack  
- **Backend:** Python, Django, Django REST Framework (DRF)  
- **Frontend:** HTML, CSS(fully custom, responsive design), JavaScript, AJAX  
- **Database:** SQLite
- **Real-time Functionality:** Django Channels (WebSockets)  
- **Authentication:** Django’s built-in authentication system with role-based access

### 🏗️ Architectural Design  

#### **Role-Based System**  
- Unlike simpler applications with a single user type, this platform **supports two roles** with distinct dashboards and permissions:  
  - **Students:** Track progress, watch lectures, complete assignments, take quizzes, and resume lessons.  
  - **Instructors:** Manage courses and lessons, grade assignments, send announcements, and monitor student performance.  


#### **Modular App Structure**  
- The project follows a **multi-app Django structure** for separation of concerns:  
  - `users` – Handles general-purpose functionality, including user authentication, anonymous browsing, viewing and enrolling in courses. It also manages shared models used across the project and the WebSocket configuration.
  - `learning` – Manages functionality and features available to students after enrolling in at least one course. 
  - `teaching` – Instructor-specific functionality: tools to manage courses, lessons, view/grade assignments and interact with students.  

#### **Database Design & Optimization**  
- **15+ models** structured for clarity, avoiding bloated tables.  
- **Through-model (LessonCompletion)** tracks student progress without bloating the `Lesson` model.  
- **Efficient Many-to-Many relationships** (e.g., courses categorized into multiple fields of study as well as levels).  
- **Custom model methods** simplify repetitive calculations (e.g., progress tracking, average grades).  

#### **Frontend & UX Enhancements**  
- **AJAX-powered interactivity**: Inline editing, UI/UX togglers, quiz timers, page updates without reloads.  
- **PDF.js integration**: View assignments directly in the browser without downloading.  
- **Custom CSS & media queries** for a fully responsive, mobile-friendly design.  

#### **Real-Time Features**  
- **WebSocket-based notifications** enable live updates for instructor announcements. Unlike traditional chat-based systems, this ensures focused, education-relevant communication.  

#### **Quizzes & Interactive Learning**  
- Dynamic **quiz system** with:  
  - One-question-per-card UX for better focus  
  - **Real-time feedback** (answer comparison & scores)  
  - **Timer system** with automatic submission on timeout  
  - Progress tracking while taking a quiz

---
##  Key Features  

###  Intuitive Learning Experience  
- **Smart dashboard system** tailored separately for **students** and **instructors**.   
-  **Modern, responsive and user-friendly UI** with an engaging **home page** featuring testimonials, FAQs and dynamic elements.
- **Dynamic course catalog** with **filtering options** (by category, level).  
- **Comprehensive course pages** including syllabus, instructor details, and user reviews.  
- **Smooth lesson navigation** with:  
  - Embedded video player  
  - Downloadable resources  
  - Homework Requirements & Assignment Submission

### Assignments & Grading  
- **PDF-based homework submissions** with in-app viewing for instructors.  
- **Grading system** that allows instructors to dynamically update scores.  

### Advanced Features  
- **Live notifications via WebSockets** (to send real-time messages from instructors to students).  
- **Interactive quiz system** with:  
  - Timed assessments  
  - Instant feedback & score tracking  
- Course and Lesson management with **inline editing (AJAX) and Django REST API support**


---
## ⚙️ Key Design Decisions  

- **Centralized Models:** Kept models in a single `models.py` since they are tightly connected, reducing unnecessary complexity.  
- **User & Profile Separation:** Split authentication data (`User`) from user-specific details (`Profile`) for flexibility in role-based permissions.  
- **Test Strategy:** Focused on feature workflows instead of redundant per-view tests. Currently excludes WebSocket & JavaScript-dependent features.  
- **Views Approach:** Used a mix of FBVs, CBVs, and DRF to demonstrate adaptability:
    - FBVs for fundamental logic control.
    - CBVs for reusable & structured views.
    - DRF for API-driven interactions.  
- **Mix of Server-Rendered & API Views:**  
    - Forms & file uploads → traditional Django views.  
    - Dynamic updates & inline editing → DRF APIs.  

