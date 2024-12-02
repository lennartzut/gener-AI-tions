// Function to toggle the display of death-related fields
function toggleDeathFields() {
    const isDeceased = document.getElementById('isDeceased').checked;
    const isDeceasedUnknown = document.getElementById('isDeceasedUnknown').checked;
    const deathFields = document.getElementById('deathFields');

    // Show death fields only if "Deceased" is checked and "Unknown" is not
    deathFields.style.display = (isDeceased && !isDeceasedUnknown) ? 'block' : 'none';
}

// Event listener for adding a new identity form
document.getElementById('addIdentityBtn').addEventListener('click', function () {
    const identitySection = document.getElementById('identitySection');

    // Fetch and append the identity form template from a hidden template element
    const template = document.getElementById('identityFormTemplate');
    const clone = template.content.cloneNode(true);
    identitySection.appendChild(clone);

    // Attach remove event to the newly added "Remove Identity" button
    const removeBtn = identitySection.querySelector('.remove-identity:last-of-type');
    if (removeBtn) {
        removeBtn.addEventListener('click', function () {
            removeBtn.closest('.identity-fields').remove();
        });
    }
});

// Event listener for submitting the individual form
document.getElementById('addIndividualForm').addEventListener('submit', async function (event) {
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
                // Adjusted regex to correctly extract field names
                const match = input.name.match(/\[(\w+)\]$/);
                if (match) {
                    const fieldName = match[1];
                    identityData[fieldName] = input.value;
                }
            }
        });
        if (Object.keys(identityData).length > 0) {
            individualData.identities.push(identityData);
        }
    });

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

            // Append the new individual to the list
            appendIndividualToList(newIndividual);

            // Close the modal
            const modalElement = document.getElementById('addIndividualModal');
            const modalInstance = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
            modalInstance.hide();

            // Reset the form
            this.reset();
            toggleDeathFields(); // Reset the death fields visibility

            alert('Individual added successfully!');
        } else {
            let data;
            try {
                data = await response.json();
            } catch (e) {
                console.error('Error parsing JSON:', e);
                data = null;
            }
            if (data && data.error) {
                alert('Error: ' + data.error); // Display error message from the server
            } else {
                alert('An error occurred. Please try again.');
            }
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An unexpected error occurred. Please try again.');
    }
});

// Function to append the new individual to the list
function appendIndividualToList(individual) {
    const listGroup = document.querySelector('.list-group');

    const listItem = document.createElement('li');
    listItem.className = 'list-group-item';

    const link = document.createElement('a');
    link.href = `/individuals/${individual.id}/family-card`;
    link.className = 'text-decoration-none';
    link.textContent = individual.name;

    listItem.appendChild(link);
    listGroup.appendChild(listItem);
}
