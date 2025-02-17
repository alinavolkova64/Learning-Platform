// Function to handle grade button click
function initializeGradeButtonClick() {
    document.querySelectorAll('.grade-button').forEach(button => {
        button.addEventListener('click', (e) => {
            const assignmentCard = e.target.closest('.assignment-card');
            const gradeInput = assignmentCard.querySelector('.grade-input');
            const saveButton = assignmentCard.querySelector('.save-grade-button');

            // Show input and save button
            gradeInput.style.display = 'inline-block';
            saveButton.style.display = 'inline-block';
            button.style.display = 'none';
        });
    });
}

// Function to handle save grade for student's assignment
function initializeSaveGradeButtonClick() {
    document.querySelectorAll('.save-grade-button').forEach(button => {
        button.addEventListener('click', async (e) => {
            const assignmentCard = e.target.closest('.assignment-card');
            const gradeInput = assignmentCard.querySelector('.grade-input');
            const grade = gradeInput.value;
            const assignmentId = assignmentCard.getAttribute('data-assignment-id');

            if (grade === '' || isNaN(grade) || grade < 0 || grade > 10) {
                alert('Please enter a valid grade between 0 and 10.');
                return;
            }

            try {
                const response = await fetch(`/teaching/api/student-assignments/${assignmentId}/grade/`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify({ grade: parseInt(grade) }),
                });

                if (response.ok) {
                    alert('Grade updated successfully!');
                    // Optionally, update the UI to reflect the new grade
                    gradeInput.style.display = 'none';
                    button.style.display = 'none';
                    assignmentCard.querySelector('.save-grade-button').style.display = 'none';
                    // show the grade 
                    const gradeDisplay = document.createElement('span');
                    gradeDisplay.textContent = `Grade: ${grade}`;
                    assignmentCard.appendChild(gradeDisplay);
                } else {
                    const errorData = await response.json();
                    alert(`Error: ${errorData.error || 'Failed to update grade.'}`);
                }
            } catch (error) {
                console.error('Error updating grade:', error);
                alert('An error occurred while updating the grade.');
            }
        });
    });
}


// Function to handle saving course changes
function initializeSaveCourseButton() {
    const saveButton = document.getElementById('save-course-changes'); // Make sure your button has this ID

    if (saveButton) {
        saveButton.addEventListener('click', async (event) => {
            event.preventDefault();  // Prevent default button behavior

            const courseId = document.getElementById('course-edit').dataset.courseId;  

            if (!courseId) {
                alert("Course ID not found.");
                return;
            }

            const jsonData = getFormDataAsJson('course-edit');

            try {
                const response = await fetch(`/teaching/api/courses/${courseId}/save_course_changes/`, {
                    method: 'PUT',
                    body: JSON.stringify(jsonData),
                    headers: {
                        'Content-Type': 'application/json', 
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value // CSRF token for security
                    }
                });

                if (response.ok) {
                    const updatedCourse = await response.json();

                    // Update the UI with the new course data
                    document.querySelector('#course-title').textContent = updatedCourse.title;
                    document.querySelector('#course-description').textContent = updatedCourse.description;
                    document.querySelector('#course-level').textContent = updatedCourse.level;

                    toggleEditCourse(); // Hide editing interface
                } else {
                    const errorData = await response.json();
                    alert(`Error: ${errorData.error || 'Failed to save course changes.'}`);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to update course');
            }
        });
    }
}


// Function to handle submission of course creation form 
function initializeCreateCourseForm() {
    const createCourseForm = document.getElementById('create-course-form');

    if (createCourseForm) {
        createCourseForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const jsonData = getFormDataAsJson('create-course-form', true);

            try {
                const response = await fetch('/teaching/api/courses/create_course/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    },
                    body: JSON.stringify(jsonData),
                });

                if (response.ok) {
                    alert('Course created successfully!');
                    window.location.href = '/teaching/instructor-dashboard/';
                } else {
                    const errorData = await response.json();
                    alert(`Error: ${errorData.error || 'Failed to create course.'}`);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to create course');
            }
        });
    }
}

// Helper function to get form data as JSON
function getFormDataAsJson(formId, isCreateCourse = false) {
    const formData = new FormData(document.getElementById(formId));
    const jsonData = {};

    formData.forEach((value, key) => {
        // Convert field_of_study to a number if it's for the create course form
        if (isCreateCourse && key === 'field_of_study') {
            jsonData[key] = Number(value);
        } else {
            jsonData[key] = value;
        }
    });

    return jsonData;
}


// Handles dynamic submission of announcement form from instructor's page
function initializeAnnouncementForm() {
    const form = document.getElementById("announcement-form");

    if (form) {
        form.addEventListener("submit", async function (e) {
            e.preventDefault(); // Prevent the default form submission behavior
    
            const formData = new FormData(form); // Collect form data
            const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
    
            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken,
                    },
                    body: formData,
                });
    
                const data = await response.json();
    
                if (response.ok) {
                    alert(data.message); // Show success message
                    form.reset(); // Clear the form fields
                } else {
                    alert(`Error: ${data.error || "Something went wrong."}`);
                }
            } catch (error) {
                console.error("Error sending announcement:", error);
                alert("Failed to send announcement. Please try again.");
            }
        });
    }
}


document.addEventListener('DOMContentLoaded', () => {
    initializeSaveCourseButton();
    initializeCreateCourseForm();
    initializeGradeButtonClick();
    initializeSaveGradeButtonClick();
    initializeAnnouncementForm();
});