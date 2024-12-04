// Function to toggle the display of death-related fields
function toggleDeathFields() {
    const isDeceased = document.getElementById('isDeceased')?.checked;
    const isDeceasedUnknown = document.getElementById('isDeceasedUnknown')?.checked;
    const deathFields = document.getElementById('deathFields');

    if (deathFields) {
        deathFields.style.display = (isDeceased && !isDeceasedUnknown) ? 'block' : 'none';
    }
}

// Ensure the DOM is fully loaded before running the script
document.addEventListener('DOMContentLoaded', function () {
    const addIdentityBtn = document.getElementById('addIdentityBtn');
    const addIndividualForm = document.getElementById('addIndividualForm');

    // Function to create and append a new field from a template
    function createNewField(templateId, containerId) {
        const template = document.getElementById(templateId);
        const container = document.getElementById(containerId);

        if (template && container) {
            const clone = template.content.cloneNode(true);
            container.appendChild(clone);

            // Attach remove event to the "Remove Identity" button
            const removeBtn = container.querySelector('.remove-identity:last-of-type');
            if (removeBtn) {
                removeBtn.addEventListener('click', function () {
                    removeBtn.closest('.identity-fields').remove();
                });
            }
        } else {
            console.error(`Template or container not found: ${templateId}, ${containerId}`);
        }
    }

    // Event listener for adding a new identity form
    if (addIdentityBtn) {
        addIdentityBtn.addEventListener('click', function () {
            createNewField('identityFormTemplate', 'identitySection');
        });
    }

    // Event listener for submitting the individual form
    if (addIndividualForm) {
        addIndividualForm.addEventListener('submit', async function (event) {
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

// Function to append the new individual to the list
function appendIndividualToList(individual) {
    const listGroup = document.querySelector('.list-group');

    if (listGroup) {
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item';

        const link = document.createElement('a');
        link.href = `/individuals/${individual.id}/family-card`;
        link.className = 'text-decoration-none';
        link.textContent = individual.name;

        listItem.appendChild(link);
        listGroup.appendChild(listItem);
    } else {
        console.error('List group not found.');
    }
}
