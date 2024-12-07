import { toggleDeathFields } from './common.js';

document.addEventListener('DOMContentLoaded', function () {
    // Initialize death fields toggle functionality
    toggleDeathFields();

    const isDeceasedCheckbox = document.getElementById('isDeceased');
    const isDeceasedUnknownCheckbox = document.getElementById('isDeceasedUnknown');

    if (isDeceasedCheckbox) {
        isDeceasedCheckbox.addEventListener('change', function () {
            // Untoggle the other checkbox to prevent conflicts
            if (isDeceasedUnknownCheckbox.checked) {
                isDeceasedUnknownCheckbox.checked = false;
            }
            toggleDeathFields();
        });
    }

    if (isDeceasedUnknownCheckbox) {
        isDeceasedUnknownCheckbox.addEventListener('change', function () {
            // Untoggle the other checkbox to prevent conflicts
            if (isDeceasedCheckbox.checked) {
                isDeceasedCheckbox.checked = false;
            }
            toggleDeathFields();
        });
    }

    // Form submission for adding an individual
    const addIndividualForm = document.getElementById('addIndividualForm');
    if (addIndividualForm) {
        addIndividualForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            const formData = new FormData(this);

            // Prepare individual data for submission
            const individualData = {
                birth_date: formData.get('birth_date') || null, // Convert empty strings to null
                birth_place: formData.get('birth_place') || null,
                death_date: formData.get('death_date') || null, // Convert empty strings to null
                death_place: formData.get('death_place') || null,
                first_name: formData.get('first_name') || null,
                last_name: formData.get('last_name') || null,
                gender: formData.get('gender') || null,
                user_id: formData.get('user_id') || null,
            };

            // If "Deceased Unknown" is checked, explicitly set death fields to null
            if (isDeceasedUnknownCheckbox && isDeceasedUnknownCheckbox.checked) {
                individualData.death_date = null;
                individualData.death_place = null;
            }

            console.log('Submitting individual data:', individualData); // Debugging log

            // Basic client-side validation
            if (!individualData.first_name || !individualData.last_name || !individualData.gender) {
                alert('Please fill out all required fields: First Name, Last Name, and Gender.');
                return;
            }

            try {
                // Make the API request to add an individual
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
                    console.log('New individual created:', newIndividual);
                    location.reload(); // Reload the page to show the updated individual list
                } else {
                    const data = await response.json();
                    console.error('Error response:', data);
                    alert(data.error || 'An error occurred. Please try again.');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An unexpected error occurred. Please try again.');
            }
        });
    }
});
