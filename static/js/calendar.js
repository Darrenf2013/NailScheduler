document.addEventListener('DOMContentLoaded', function() {
    // Initialize the calendar
    const calendarEl = document.getElementById('calendar');
    
    if (!calendarEl) return;
    
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        slotDuration: '00:30:00', // 30 minute slots
        slotMinTime: '08:00:00',  // Start at 8am
        slotMaxTime: '20:00:00',  // End at 8pm
        height: 'auto',
        allDaySlot: false,
        nowIndicator: true,
        navLinks: true,
        selectable: true,
        selectMirror: true,
        dayMaxEvents: true,
        timeZone: 'local',
        
        // Event data source
        events: {
            url: '/api/calendar-events',
            method: 'GET',
            failure: function() {
                showAlert('Error', 'There was an error loading events', 'danger');
            }
        },
        
        // Event handlers
        select: function(info) {
            // Handle new time slot or appointment creation
            const startTime = info.start;
            const endTime = info.end;
            
            // Format date for modal
            const dateStr = startTime.toISOString().substring(0, 10);
            const startTimeStr = startTime.toISOString().substring(11, 16);
            const endTimeStr = endTime.toISOString().substring(11, 16);
            
            // Set values in modal
            document.getElementById('new-slot-date').value = dateStr;
            document.getElementById('new-slot-start-time').value = startTimeStr;
            document.getElementById('new-slot-end-time').value = endTimeStr;
            
            // Show modal for creating a new slot
            const slotModal = new bootstrap.Modal(document.getElementById('new-slot-modal'));
            slotModal.show();
            
            // Clear selection
            calendar.unselect();
        },
        
        eventClick: function(info) {
            // Handle event click
            const event = info.event;
            const eventType = event.extendedProps.type;
            
            if (eventType === 'appointment') {
                // Redirect to appointment details
                const appointmentId = event.extendedProps.appointmentId;
                window.location.href = `/appointment/${appointmentId}`;
            } else if (eventType === 'slot') {
                // Show modal for slot management
                const slotId = event.extendedProps.slotId;
                
                // Set values in modal
                document.getElementById('manage-slot-id').value = slotId;
                
                // Show modal
                const manageSlotModal = new bootstrap.Modal(document.getElementById('manage-slot-modal'));
                manageSlotModal.show();
            }
        }
    });
    
    calendar.render();
    
    // Add event listeners for modal actions
    setupModalEventListeners(calendar);
});

function setupModalEventListeners(calendar) {
    // New slot form submission
    const newSlotForm = document.getElementById('new-slot-form');
    if (newSlotForm) {
        newSlotForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const date = document.getElementById('new-slot-date').value;
            const startTime = document.getElementById('new-slot-start-time').value;
            const endTime = document.getElementById('new-slot-end-time').value;
            
            // Send request to create new slot
            axios.post('/schedule', {
                action: 'add_slot',
                date: date,
                start_time: startTime,
                end_time: endTime
            })
            .then(function(response) {
                if (response.data.success) {
                    // Close modal
                    bootstrap.Modal.getInstance(document.getElementById('new-slot-modal')).hide();
                    
                    // Show success message
                    showAlert('Success', 'Time slot added successfully', 'success');
                    
                    // Refresh calendar
                    calendar.refetchEvents();
                } else {
                    showAlert('Error', response.data.message, 'danger');
                }
            })
            .catch(function(error) {
                showAlert('Error', 'An error occurred while adding the time slot', 'danger');
                console.error(error);
            });
        });
    }
    
    // Manage slot actions
    const removeSlotBtn = document.getElementById('remove-slot-btn');
    if (removeSlotBtn) {
        removeSlotBtn.addEventListener('click', function() {
            const slotId = document.getElementById('manage-slot-id').value;
            
            // Confirm deletion
            if (confirm('Are you sure you want to remove this time slot?')) {
                // Send request to remove slot
                axios.post('/schedule', {
                    action: 'remove_slot',
                    slot_id: slotId
                })
                .then(function(response) {
                    if (response.data.success) {
                        // Close modal
                        bootstrap.Modal.getInstance(document.getElementById('manage-slot-modal')).hide();
                        
                        // Show success message
                        showAlert('Success', 'Time slot removed', 'success');
                        
                        // Refresh calendar
                        calendar.refetchEvents();
                    } else {
                        showAlert('Error', response.data.message, 'danger');
                    }
                })
                .catch(function(error) {
                    showAlert('Error', 'An error occurred while removing the time slot', 'danger');
                    console.error(error);
                });
            }
        });
    }
}

function showAlert(title, message, type) {
    // Create alert container if it doesn't exist
    let alertContainer = document.getElementById('alert-container');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.id = 'alert-container';
        alertContainer.style.position = 'fixed';
        alertContainer.style.top = '20px';
        alertContainer.style.right = '20px';
        alertContainer.style.zIndex = '9999';
        document.body.appendChild(alertContainer);
    }
    
    // Create alert element
    const alertEl = document.createElement('div');
    alertEl.className = `alert alert-${type} alert-dismissible fade show`;
    alertEl.innerHTML = `
        <strong>${title}:</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to container
    alertContainer.appendChild(alertEl);
    
    // Auto dismiss after 5 seconds
    setTimeout(function() {
        const bsAlert = new bootstrap.Alert(alertEl);
        bsAlert.close();
    }, 5000);
}
