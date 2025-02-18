//------------------------------    WEBSOCKET    ----------------------------------------- 
const notifySocket = new WebSocket( // setup chat socket
    'wss://' // ensure secure connection
    + window.location.host
    + '/ws/notify/'
);  

// on socket open
notifySocket.onopen = function(e) {
    console.log('Socket successfully connected.');

    // Fetch and update the notification count as soon as connection is established
    newNotificationsCount();
};

// on socket close
notifySocket.onclose = function(e) {
    console.log('Socket closed.');
};

// on error
notifySocket.onerror = function(e) {
    console.error('WebSocket error:', e);
};

// on receiving message
notifySocket.onmessage = function(e) {
   // Fetch and update the notification count to get notifications in real time
    newNotificationsCount();
};
//------------------------------------------------------------------------------------------



// Sets the new number for unread notifications
function newNotificationsCount() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const bellCount = document.getElementById('bellCount');

    if (bellCount) {
        // Fetch the count of new notifications
        fetch('/learning/new-notifications-count/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            const newCount = data.new_notifications_count;
            
            // Update the data-count attribute
            bellCount.setAttribute('data-count', newCount);
        })
        .catch(error => {
            console.error('Error fetching notifications count:', error);
        });
    }
}


// Marks notifications as read after opening notification dropdown
function markNotificationsRead() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch(`/learning/mark-notifications-read/`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Reset the new notifications count to 0
            document.getElementById('bellCount').setAttribute('data-count', 0);
        }
    })
    .catch(error => console.error('Error:', error));
};


// Opens a dropdown with all notifications for the current user
function showNotifications() {
    const notifMessages = document.getElementById('notif-messages');
    
    // Toggle visibility
    notifMessages.classList.toggle('hidden');
    notifMessages.classList.toggle('visible');
    
    // Fetch notifications only when the dropdown is being shown
    if (notifMessages.classList.contains('visible')) {
        fetch('/learning/notifications/') // Adjust the URL to your endpoint for fetching notifications
            .then(response => response.json())
            .then(data => {
                // Clear the existing notifications
                notifMessages.innerHTML = '';

                // Populate with the latest notifications
                if (data.notifications.length > 0) {
                    data.notifications.forEach(notif => {
                        const notifDiv = document.createElement('div');
                        notifDiv.classList.add('announcement');
                        notifDiv.innerHTML = `
                            <p>${notif.message}</p>
                            <p class="small">${notif.timestamp}</p>
                        `;
                        notifMessages.appendChild(notifDiv);
                    });
                } else {
                    notifMessages.innerHTML = '<p>You have no notifications.</p>';
                }
            })
            .catch(error => console.error('Error fetching notifications:', error));
    }
}


/* Sends a POST request to the backend to trigger the creation of a Notification instance
(for testing purposes, to simulate a notification being created and sent to the user). */
function triggerTestNotification() {
    fetch(window.location.href, { // Trigger a fetch request to the same URL 
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .catch(error => {
        console.error('Error:', error);
    });
};


/* Dashboard assignment section for toggling between pending and submitted */
function switchTab(tab) {
    document.querySelectorAll('.tab-content').forEach(function(content) {
        content.style.display = 'none';
    });
    document.getElementById(tab).style.display = 'block';

    document.querySelectorAll('.tab').forEach(function(tabEl) {
        tabEl.classList.remove('active');
    });
    document.querySelector('.tab[onclick="switchTab(\'' + tab + '\')"]').classList.add('active');
}


/* Allows toggling between questions and answers on the homepage */
function toggleFAQ(question) {
    question.classList.toggle('active');
    const answer = question.nextElementSibling;

    if (answer.style.maxHeight) {
        answer.style.maxHeight = null;
    } else {
        answer.style.maxHeight = answer.scrollHeight + 'px';
    }
}


/* Allows toggling between showing and hiding the answer table after quiz completion */
function toggleCorrectAnswers(button) {
    const table = document.getElementById("answersTable");
    if (table.style.display === "none" || !table.style.display) {
        table.style.display = "block";
        button.textContent = "Hide Correct Answers";
    } else {
        table.style.display = "none";
        button.textContent = "View Correct Answers";
    }
}


/* Allows toggling between showing course info and opening an editing interface for it */
function toggleEditCourse() {
    const courseDisplay = document.getElementById('course-display');
    const courseEditForm = document.getElementById('course-edit');
    button = document.getElementById('edit-button')

    // Check if the courseDisplay is hidden
    if (courseDisplay.style.display === "none" || courseDisplay.style.display === "") {
        courseDisplay.style.display = "block"; // Show the display section
        courseEditForm.style.display = "none"; // Hide the form
        button.textContent = "Edit"; 
    } else {
        courseDisplay.style.display = "none"; // Hide the display section
        courseEditForm.style.display = "block"; // Show the form
        button.textContent = "Hide Editing"; 
    }
};


// Showing or hiding assignment elements based on the selected course filter
function filterAssignments() {
    const selectedCourse = document.getElementById('course-filter').value;

    // Get all assignment elements
    const ungradedAssignments = document.querySelectorAll('#ungraded-assignments .assignment-card');
    const gradedAssignments = document.querySelectorAll('#graded-assignments tr');

    // Show or hide ungraded assignments
    ungradedAssignments.forEach(assignment => {
        if (selectedCourse === 'all' || assignment.classList.contains(`course-${selectedCourse}`)) {
            assignment.style.display = 'block';
        } else {
            assignment.style.display = 'none';
        }
    });

    // Show or hide graded assignments
    gradedAssignments.forEach(assignment => {
        if (selectedCourse === 'all' || assignment.classList.contains(`course-${selectedCourse}`)) {
            assignment.style.display = '';
        } else {
            assignment.style.display = 'none';
        }
    });
}


const pdfContainer = document.getElementById("pdf-container");

// Function to render the PDF submitted by students in assignment
const renderPDF = async (url) => {
    pdfContainer.style.display = "block"; // Show the container
    const pdf = await pdfjsLib.getDocument(url).promise;
    const page = await pdf.getPage(1); // Load the first page

    // Create a canvas to render the PDF page
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");
    pdfContainer.innerHTML = ""; // Clear previous content
    pdfContainer.appendChild(canvas);

    // Set up the viewport for the PDF
    const viewport = page.getViewport({ scale: 1 }); 
    canvas.width = viewport.width;
    canvas.height = viewport.height;

    const renderContext = {
        canvasContext: context,
        viewport: viewport,
    };
    await page.render(renderContext).promise;
};


// Redirects student to the first lesson after successful enrollment
function enroll(event) {
    event.preventDefault(); // Prevent default form submission behavior
    const enrollForm = document.getElementById('enroll-form');
    let courseTitle = enrollForm.getAttribute('data-course-title');
    let courseId = parseInt(enrollForm.getAttribute('data-course-id'));
    
    console.log(`Title: ${courseTitle}`)

    fetch(`/enroll/${courseId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log(`Data: ${data}`)
        if (data.success) {
            window.location.href = `/learning/lesson/${courseTitle}/1/`
        } else {
            // Handle error messages
            alert(data.message || 'An error occurred during enrollment.');
        }
    })
    .catch(error => console.error('Error:', error));
};


document.addEventListener("DOMContentLoaded", function () {
    
    // Notification dropdown
    const notifHeader = document.getElementById('notif-header');
    if (notifHeader) {
        notifHeader.addEventListener('click', function () {
            showNotifications(); // Fetch and display notifications
            markNotificationsRead();
        });
    }

    // FAQ Toggle Event Listeners
    const faqQuestions = document.querySelectorAll('.faq-question');
    faqQuestions.forEach(question => {
        question.addEventListener('click', () => toggleFAQ(question));
    });

    // Correct Answers Toggle Event Listener
    const toggleButton = document.getElementById("toggleAnswers");
    if (toggleButton) {
        toggleButton.addEventListener("click", () => toggleCorrectAnswers(toggleButton));
    }

    // Toggle between viewing course info and editing it
    const editCourseBtn = document.getElementById('edit-button');
    if (editCourseBtn) {
        editCourseBtn.addEventListener('click', function (e) {
            e.preventDefault(); // Prevent default anchor behavior
            toggleEditCourse();
        });
    }

    // Trigger fake notification creation 
    const testNotifBtn = document.getElementById('testNotificationButton')
    if (testNotifBtn) {
        testNotifBtn.addEventListener('click', () => triggerTestNotification());
    }

    // Showing or hiding assignment elements based on the selected course filter, when change is detected
    const courseFilter = document.getElementById('course-filter');
    if (courseFilter) {
        courseFilter.addEventListener('change', () => filterAssignments());
    }

    // Enrolling in a course
    const enrollForm = document.getElementById('enroll-form');
    if (enrollForm) {
        enrollForm.addEventListener('submit', (event) => enroll(event));
    }

    // Showing or hiding assignment PDF
    if (pdfContainer) {
        // Event listener for the "View" button
        document.querySelectorAll(".view-pdf-button").forEach((button) => {
            button.addEventListener("click", async function () {
                const assignmentId = this.getAttribute("data-assignment-id");

                if (pdfContainer.style.display === "none") {
                    pdfContainer.style.display = "block";
                    button.textContent = "Hide PDF";

                    // Fetch the file URL from the API
                    try {
                        const response = await fetch(`/teaching/assignment/${assignmentId}/file/`);
                        if (!response.ok) throw new Error("Failed to fetch file URL");
                        const data = await response.json();

                        // Render the PDF
                        await renderPDF(data.file_url);
                    } catch (error) {
                        console.error("Error loading PDF:", error);
                        alert("Failed to load the PDF. Please try again.");
                    }
                } else {
                    pdfContainer.style.display = "none";
                    button.textContent = "View PDF";
                    pdfContainer.innerHTML = ""; // Clear the container (remove canvas)
                }
            });
        });
        };
});