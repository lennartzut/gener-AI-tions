function toggleDeathFields() {
    const isDeceased = document.getElementById('isDeceased').checked;
    const isDeceasedUnknown = document.getElementById('isDeceasedUnknown').checked;
    const deathFields = document.getElementById('deathFields');

    // Show death fields only if "Deceased" is checked and "Unknown" is not
    deathFields.style.display = (isDeceased && !isDeceasedUnknown) ? 'block' : 'none';
}

document.getElementById('addIdentityBtn').addEventListener('click', function () {
    const identitySection = document.getElementById('identitySection');

    // Fetch and append the identity form template
    fetch('/static/templates/partials/forms/identity_form.html')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load identity form template');
            }
            return response.text();
        })
        .then(html => {
            const template = document.createElement('div');
            template.innerHTML = html;
            identitySection.appendChild(template);

            // Attach remove event to the newly added "Remove Identity" button
            template.querySelector('.remove-identity').addEventListener('click', function () {
                template.remove();
            });
        })
        .catch(error => {
            console.error('Error loading identity form:', error);
            alert('Could not add identity field. Please try again.');
        });
});

document.getElementById('addIndividualForm').addEventListener('submit', function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    const individualData = {
        birth_date: formData.get('birth_date'),
        birth_place: formData.get('birth_place'),
        death_date: formData.get('death_date'),
        death_place: formData.get('death_place'),
        first_name: formData.get('first_name'), // First name for the default identity
        last_name: formData.get('last_name'),   // Last name for the default identity
        gender: formData.get('gender'),        // Gender for the default identity
        identities: [] // Additional identities will be added dynamically
    };

    // Extract additional identity data from dynamically added identity forms
    document.querySelectorAll('.identity-fields').forEach(fieldset => {
        const identityData = {};
        fieldset.querySelectorAll('input, select').forEach(input => {
            if (input.value) {
                identityData[input.name.split('[')[2].replace(']', '')] = input.value;
            }
        });
        if (Object.keys(identityData).length > 0) {
            individualData.identities.push(identityData);
        }
    });

    // Submit the data via API
    fetch('/api/individuals', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(individualData),
        credentials: 'include'  // Important to include cookies
    })

        .then(response => {
            if (response.ok) {
                location.reload(); // Reload the page on successful submission
            } else if (response.status === 401) {
                alert('Unauthorized. Please log in again.');
                window.location.href = '/auth/login'; // Redirect to login page
            } else {
                return response.json(); // Parse and handle errors
            }
        })
        .then(data => {
            if (data && data.error) {
                alert(data.error); // Display error message
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while saving the individual. Please try again.');
        });
});
