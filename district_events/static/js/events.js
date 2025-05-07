document.addEventListener('DOMContentLoaded', function() {
    const eventsContainer = document.getElementById('events-container');
    if (eventsContainer) {
        eventsContainer.addEventListener('click', function(event) {
            if (event.target.classList.contains('delete-btn')) {
                const eventId = event.target.dataset.eventId;
                deleteEvent(eventId);
            } else if (event.target.classList.contains('edit-btn')) {
                const eventId = event.target.dataset.eventId;
                openEditModal(eventId);
            }
        });
    }

    const editModal = document.getElementById('edit-modal');
    const editForm = document.getElementById('edit-form');
    const cancelEditBtn = document.getElementById('cancel-edit');

    if (editModal && editForm && cancelEditBtn) {
        cancelEditBtn.addEventListener('click', () => {
            editModal.style.display = 'none';
        });

        editForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const eventId = document.getElementById('edit-event-id').value;
            const title = document.getElementById('edit-title').value;
            const description = document.getElementById('edit-description').value;
            saveEditedEvent(eventId, title, description);
        });
    }
});

function deleteEvent(eventId) {
    if (confirm('Are you sure you want to delete this event?')) {
        fetch(`/api/admin/events/${eventId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Event deleted successfully') {
                const eventDiv = document.querySelector(`.event-item[data-event-id="${eventId}"]`);
                if (eventDiv) {
                    eventDiv.remove();
                }
            } else {
                alert('Error deleting event: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error deleting event:', error);
            alert('Failed to delete event.');
        });
    }
}

function openEditModal(eventId) {
    fetch(`/api/events`) // Assuming your public API returns all event details
        .then(response => response.json())
        .then(events => {
            const eventToEdit = events.find(event => event.id === parseInt(eventId));
            if (eventToEdit) {
                document.getElementById('edit-event-id').value = eventToEdit.id;
                document.getElementById('edit-title').value = eventToEdit.title;
                document.getElementById('edit-description').value = eventToEdit.description;
                document.getElementById('edit-modal').style.display = 'block';
            } else {
                alert('Could not find event for editing.');
            }
        })
        .catch(error => {
            console.error('Error fetching event details:', error);
            alert('Failed to fetch event details for editing.');
        });
}

function saveEditedEvent(eventId, title, description) {
    fetch(`/api/admin/events/${eventId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title: title, description: description })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Event updated successfully') {
            const eventDiv = document.querySelector(`.event-item[data-event-id="${eventId}"] h3`);
            if (eventDiv) {
                eventDiv.textContent = title;
                const descDiv = document.querySelector(`.event-item[data-event-id="${eventId}"] p`);
                if (descDiv) {
                    descDiv.textContent = description;
                }
                document.getElementById('edit-modal').style.display = 'none';
            }
        } else {
            alert('Error updating event: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error updating event:', error);
        alert('Failed to update event.');
    });
}