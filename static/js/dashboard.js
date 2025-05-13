document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Quick reply functionality for message cards
    const quickReplyBtns = document.querySelectorAll('.quick-reply-btn');
    quickReplyBtns.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const threadId = this.getAttribute('data-thread-id');
            const responseType = this.getAttribute('data-response');
            
            // Get response text based on type
            let responseText = '';
            switch(responseType) {
                case 'yes':
                    responseText = "Yes, I'm available at that time. I'll schedule you in!";
                    break;
                case 'no':
                    responseText = "I'm sorry, I'm not available at that time. Could you suggest a different day or time?";
                    break;
                case 'info':
                    responseText = "I offer a variety of nail services. My basic manicure is $30, gel polish is $45. Would you like me to book you for an appointment?";
                    break;
                default:
                    responseText = "Thank you for your message. I'll get back to you soon!";
            }
            
            // Send response
            axios.post(`/message/${threadId}`, {
                message: responseText
            })
            .then(function(response) {
                window.location.href = `/message/${threadId}`;
            })
            .catch(function(error) {
                console.error(error);
                alert('Failed to send response');
            });
        });
    });
    
    // Appointment status updates
    const statusUpdateBtns = document.querySelectorAll('.status-update-btn');
    statusUpdateBtns.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const appointmentId = this.getAttribute('data-appointment-id');
            const newStatus = this.getAttribute('data-status');
            
            // Confirm status change
            if (confirm(`Are you sure you want to mark this appointment as ${newStatus}?`)) {
                // Create form data
                const formData = new FormData();
                formData.append('action', 'update');
                formData.append('status', newStatus);
                
                // Send request
                axios.post(`/appointment/${appointmentId}`, formData)
                .then(function(response) {
                    // Refresh page to show updated status
                    window.location.reload();
                })
                .catch(function(error) {
                    console.error(error);
                    alert('Failed to update appointment status');
                });
            }
        });
    });
    
    // Initialize date pickers
    const datePickers = document.querySelectorAll('.datepicker');
    if (datePickers.length > 0) {
        datePickers.forEach(function(picker) {
            picker.addEventListener('change', function() {
                // If this is part of a filter form, submit the form
                const form = this.closest('form');
                if (form && form.classList.contains('filter-form')) {
                    form.submit();
                }
            });
        });
    }
});
