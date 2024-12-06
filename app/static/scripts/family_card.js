import { setupIndividualSearch } from './common.js';

document.addEventListener('DOMContentLoaded', function () {
    // Function to show modal for creating new individuals (generic function)
    function showCreateIndividualModal(relationshipType, relatedIndividualId, familyId = null) {
        const createIndividualModal = new bootstrap.Modal(document.getElementById('createIndividualModal'));
        const createIndividualForm = document.getElementById('createIndividualForm');
        const modalTitle = document.getElementById('createIndividualModalLabel');
        const submitButton = createIndividualForm.querySelector('button[type="submit"]');

        // Set form action based on relationship type and IDs
        let actionUrl = `/api/individuals?relationship=${relationshipType}&related_individual_id=${relatedIndividualId}`;
        if (familyId) {
            actionUrl += `&family_id=${familyId}`;
        }
        createIndividualForm.action = actionUrl;

        // Set modal title and submit button text based on the relationship type
        modalTitle.textContent = `Create New ${relationshipType.charAt(0).toUpperCase() + relationshipType.slice(1)}`;
        submitButton.textContent = `Create ${relationshipType.charAt(0).toUpperCase() + relationshipType.slice(1)}`;

        createIndividualModal.show();
    }

    // Identity selection
    const identitySelect = document.getElementById('identitySelect');
    if (identitySelect) {
        identitySelect.addEventListener('change', function() {
            const identityId = this.value;
            const url = new URL(window.location.href);
            url.searchParams.set('identity_id', identityId);
            window.location.href = url.toString();
        });
    }

    // Partner selection
    const partnerSelect = document.getElementById('partnerSelect');
    if (partnerSelect) {
        partnerSelect.addEventListener('change', function() {
            const partnerId = this.value;
            const url = new URL(window.location.href);
            url.searchParams.set('partner_id', partnerId);
            window.location.href = url.toString();
        });
    }

    // Form change detection
    const individualForm = document.getElementById('individualForm');
    const updateBtn = document.getElementById('updateIndividualBtn');
    if (individualForm && updateBtn) {
        individualForm.addEventListener('input', function() {
            updateBtn.disabled = false;
        });
    }

    // Show add parent modal
    const addParentBtn = document.getElementById('addParentBtn');
    if (addParentBtn) {
        addParentBtn.addEventListener('click', function () {
            showCreateIndividualModal('parent', "{{ individual.id }}");
        });
    }

    // Show create new parent modal
    const createNewParentBtn = document.getElementById('createNewParentBtn');
    if (createNewParentBtn) {
        createNewParentBtn.addEventListener('click', function () {
            showCreateIndividualModal('parent', "{{ individual.id }}");
        });
    }

    // Show add partner modal
    const addPartnerBtn = document.getElementById('addPartnerBtn');
    if (addPartnerBtn) {
        addPartnerBtn.addEventListener('click', function () {
            const addPartnerModal = new bootstrap.Modal(document.getElementById('addPartnerModal'));
            addPartnerModal.show();
        });
    }

    // Show create new partner modal
    const createNewPartnerBtn = document.getElementById('createNewPartnerBtn');
    if (createNewPartnerBtn) {
        createNewPartnerBtn.addEventListener('click', function () {
            const individualId = document.getElementById('individualId').value; // Ensure an element has this value.
            showCreateIndividualModal('partner', individualId);
        });
    }

    // Setup search for adding child
    const createNewChildBtn = document.getElementById('createNewChildBtn');
    if (createNewChildBtn) {
        createNewChildBtn.addEventListener('click', function () {
            const familyId = "{{ selected_partner_family.id if selected_partner_family else '' }}";
            showCreateIndividualModal('child', "{{ individual.id }}", familyId);
        });
    }

    // Show add identity modal
    const addIdentityBtn = document.getElementById('addIdentityBtn');
    if (addIdentityBtn) {
        addIdentityBtn.addEventListener('click', function() {
            const addIdentityModal = new bootstrap.Modal(document.getElementById('addIdentityModal'));
            addIdentityModal.show();
        });
    }

    // Form submission handling (Convert form data to JSON and send via Fetch)
    const createIndividualForm = document.getElementById('createIndividualForm');
    if (createIndividualForm) {
        createIndividualForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            // Collect form data and convert to JSON
            const formData = new FormData(this);
            const individualData = {};
            formData.forEach((value, key) => {
                individualData[key] = value;
            });

            try {
                const response = await fetch(this.action, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',
                    body: JSON.stringify(individualData),
                });

                if (response.ok) {
                    const newIndividual = await response.json();
                    alert('Individual created successfully!');

                    // Reload the page or update UI accordingly
                    window.location.reload();
                } else {
                    const errorData = await response.json();
                    alert(errorData.error || 'An error occurred. Please try again.');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An unexpected error occurred. Please try again.');
            }
        });
    }
});
