import { setupIndividualSearch } from './common.js';

document.addEventListener('DOMContentLoaded', function () {
    // Helper function to initialize a Bootstrap Modal
    function initializeModal(modalId) {
        const modalElement = document.getElementById(modalId);
        if (!modalElement) {
            console.error(`Modal with ID "${modalId}" not found.`);
            return null;
        }
        return new bootstrap.Modal(modalElement);
    }

    function handleRelationshipAction(actionType, relationshipType, relatedIndividualId = null, familyId = null) {
        const userIdElement = document.getElementById('userId');
        if (!userIdElement) {
            console.error('User ID is missing. Ensure it is included in the form as a hidden field.');
            alert('User ID is missing. Please contact support.');
            return;
        }

        const userId = userIdElement.value;
        const modalId = `${actionType}${relationshipType.charAt(0).toUpperCase() + relationshipType.slice(1)}Modal`;
        const modal = initializeModal(modalId);

        if (!modal) return;

        modal.show();

        setupIndividualSearch({
            inputSelector: `#${relationshipType}Name`,
            suggestionsContainerSelector: `#${relationshipType}Suggestions`,
            excludeId: individualId,
            minQueryLength: 2,
            onSelect: function (individual) {
                if (individual.id === parseInt(individualId)) {
                    alert(`An individual cannot be their own ${relationshipType}.`);
                    return;
                }
                const inputField = document.getElementById(`${relationshipType}Id`);
                if (inputField) {
                    inputField.value = individual.id;
                    document.getElementById(`${relationshipType}Name`).value = individual.name;
                    document.getElementById(`${relationshipType}Suggestions`).innerHTML = '';
                }
            },
        });
    }

    function showCreateIndividualModal(relationshipType = null, relatedIndividualId = null, familyId = null) {
        const createIndividualModal = initializeModal('createIndividualModal');
        const createIndividualForm = document.getElementById('createIndividualForm');
        const modalTitle = document.getElementById('createIndividualModalLabel');
        const submitButton = createIndividualForm.querySelector('button[type="submit"]');

        if (!createIndividualModal || !createIndividualForm || !modalTitle || !submitButton) {
            console.error('Create Individual Modal elements are missing.');
            return;
        }

        let actionUrl = `/api/individuals`;
        if (relationshipType && relatedIndividualId) {
            actionUrl += `?relationship=${relationshipType}&related_individual_id=${relatedIndividualId}`;
        }
        if (familyId) {
            actionUrl += `&family_id=${familyId}`;
        }
        createIndividualForm.action = actionUrl;

        const capitalizedRelationship = relationshipType
            ? `${relationshipType.charAt(0).toUpperCase() + relationshipType.slice(1)}`
            : 'Individual';
        modalTitle.textContent = `Create New ${capitalizedRelationship}`;
        submitButton.textContent = `Create ${capitalizedRelationship}`;

        createIndividualModal.show();
    }

    const individualId = document.getElementById('individualId')?.value;

    if (!individualId && document.getElementById('familyCardPage')) {
        console.error('Individual ID is missing on the family card page.');
    }

    ['parent', 'partner', 'child'].forEach((relationshipType) => {
        const addBtn = document.getElementById(`add${relationshipType.charAt(0).toUpperCase() + relationshipType.slice(1)}Btn`);
        if (addBtn) {
            addBtn.addEventListener('click', function () {
                handleRelationshipAction('add', relationshipType);
            });
        }

        const createBtn = document.getElementById(`createNew${relationshipType.charAt(0).toUpperCase() + relationshipType.slice(1)}Btn`);
        if (createBtn) {
            createBtn.addEventListener('click', function () {
                handleRelationshipAction('create', relationshipType);
            });
        }
    });

    const addIdentityBtn = document.getElementById('addIdentityBtn');
    if (addIdentityBtn) {
        addIdentityBtn.addEventListener('click', function () {
            const addIdentityModal = initializeModal('addIdentityModal');
            if (!addIdentityModal) {
                console.error('Add Identity Modal not found.');
                return;
            }
            addIdentityModal.show();
        });
    }

    const createIndividualForm = document.getElementById('createIndividualForm');
    if (createIndividualForm) {
        createIndividualForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            const formData = new FormData(this);
            const userIdElement = document.getElementById('userId');

            if (!userIdElement) {
                console.error('User ID is missing in the form.');
                alert('User ID is missing. Please contact support.');
                return;
            }

            const userId = userIdElement.value;
            const individualData = {};
            formData.forEach((value, key) => {
                individualData[key] = value.trim() || null;
            });

            individualData.user_id = userId; // Add user_id to the payload

            console.log("Submitting form data:", individualData);

            try {
                const response = await fetch(this.action, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(individualData),
                });

                if (response.ok) {
                    alert('Individual created successfully!');
                    window.location.reload();
                } else {
                    const errorData = await response.json();
                    console.error('Error data:', errorData);
                    alert(errorData.error || 'An error occurred. Please try again.');
                }
            } catch (error) {
                console.error('Error creating individual:', error);
                alert('An unexpected error occurred. Please try again.');
            }
        });
    }

    // Ensure modals close properly and focus behavior is corrected
    document.addEventListener('hidden.bs.modal', function (event) {
        const modal = event.target;
        if (modal.getAttribute('aria-hidden') === 'true') {
            modal.removeAttribute('aria-hidden');
        }
    });
});
