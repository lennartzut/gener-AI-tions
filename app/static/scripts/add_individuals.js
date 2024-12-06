import { toggleDeathFields } from './common.js';

document.addEventListener('DOMContentLoaded', function () {
    // Initialize death fields toggle functionality
    toggleDeathFields();

    const isDeceasedCheckbox = document.getElementById('isDeceased');
    const isDeceasedUnknownCheckbox = document.getElementById('isDeceasedUnknown');

    if (isDeceasedCheckbox) {
        isDeceasedCheckbox.addEventListener('change', toggleDeathFields);
    }
    if (isDeceasedUnknownCheckbox) {
        isDeceasedUnknownCheckbox.addEventListener('change', toggleDeathFields);
    }

    // Form submission for adding an individual
    const addIndividualForm = document.getElementById('addIndividualForm');
    if (addIndividualForm) {
        addIndividualForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            const formData = new FormData(this);
            const individualData = {
                birth_date: formData.get('birth_date'),
                birth_place: formData.get('birth_place'),
                death_date: formData.get('death_date'),
                death_place: formData.get('death_place'),
                first_name: formData.get('first_name'),
                last_name: formData.get('last_name'),
                gender: formData.get('gender')
            };

            try {
                const response = await fetch('/api/individuals/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',
                    body: JSON.stringify(individualData)
                });

                if (response.ok) {
                    const newIndividual = await response.json();
                    alert('Individual added successfully!');
                    location.reload();  // Reload the page to show the updated individual list
                } else {
                    const data = await response.json();
                    alert(data.error || 'An error occurred. Please try again.');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An unexpected error occurred. Please try again.');
            }
        });
    }
});
