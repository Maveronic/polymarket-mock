// markets/static/admin/js/bet_admin.js
document.addEventListener('DOMContentLoaded', function() {
    const eventField = document.getElementById('id_event');
    const optionField = document.getElementById('id_option');

    if (eventField && optionField) {
        eventField.addEventListener('change', function() {
            const eventId = this.value;
            if (eventId) {
                // Fetch options for the selected event
                fetch(`/admin/markets/bet/option/autocomplete/?event_id=${eventId}`)
                    .then(response => response.json())
                    .then(data => {
                        // Clear existing options
                        optionField.innerHTML = '';

                        // Add new options
                        data.results.forEach(option => {
                            const optionElement = document.createElement('option');
                            optionElement.value = option.id;
                            optionElement.textContent = option.text;
                            optionField.appendChild(optionElement);
                        });
                    });
            } else {
                // If no event is selected, clear the options
                optionField.innerHTML = '';
            }
        });
    }
});