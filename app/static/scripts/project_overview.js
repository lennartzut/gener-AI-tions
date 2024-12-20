// File: static/scripts/project_overview.js

const FamilyRelationshipEnum = {
    PARENT: 'parent',
    CHILD: 'child',
    PARTNER: 'partner'
};

document.addEventListener('DOMContentLoaded', function () {
    const projectPage = document.getElementById('projectPage');
    if (!projectPage) return;

    const projectId = projectPage.dataset.projectId;
    const individualId = projectPage.dataset.individualId;

    // Dropzones at the bottom
    const bottomDropzones = document.querySelectorAll('.d-flex.justify-content-around .dropzone');

    // Relationship Lists
    const parentsList = document.getElementById('parentsList');
    const partnersList = document.getElementById('partnersList');
    const childrenList = document.getElementById('childrenList');

    // Individuals List (for removal drop)
    const individualsList = document.getElementById('leftIndividualsList');

    // Function to fetch and render relationships
    async function fetchAndRenderRelationships() {
        if (!individualId) return;

        try {
            const response = await fetch(`/api/relationships/individual/${individualId}?project_id=${encodeURIComponent(projectId)}`, {
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch relationships');
            }

            const data = await response.json();
            const relationships = data.relationships;

            // Populate Parents List
            populateRelationshipList(parentsList, relationships.parents, 'parent');

            // Populate Partners List
            populateRelationshipList(partnersList, relationships.partners, 'partner');

            // Populate Children List
            populateRelationshipList(childrenList, relationships.children, 'child');

            // Exclude related individuals from the left list
            excludeRelatedIndividuals(relationships);
        } catch (error) {
            console.error('Error fetching relationships:', error);
        }
    }

    // Function to populate a relationship list
    function populateRelationshipList(listElement, relationships, relationshipType) {
        listElement.innerHTML = ''; // Clear existing list

        if (relationships.length > 0) {
            relationships.forEach(rel => {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
                listItem.setAttribute('draggable', 'true');
                listItem.dataset.relationshipId = rel.relationship_id;
                listItem.dataset.individualId = rel.id;

                listItem.innerHTML = `
                    <span>${rel.name}</span>
                    <small class="text-muted">ID: ${rel.id}</small>
                `;

                // Add drag event listeners for removal
                listItem.addEventListener('dragstart', handleRelationshipDragStart);

                listElement.appendChild(listItem);
            });
        } else {
            const noRelItem = document.createElement('li');
            noRelItem.className = 'list-group-item text-muted';
            noRelItem.textContent = `No ${capitalizeFirstLetter(relationshipType)}s assigned.`;
            listElement.appendChild(noRelItem);
        }
    }

    // Function to capitalize first letter
    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }

    // Function to exclude related individuals from the left list
    function excludeRelatedIndividuals(relationships) {
        const relatedIds = [
            ...relationships.parents.map(rel => rel.id),
            ...relationships.partners.map(rel => rel.id),
            ...relationships.children.map(rel => rel.id)
        ];

        const individualItems = individualsList.querySelectorAll('li.list-group-item');
        individualItems.forEach(item => {
            const indivId = parseInt(item.dataset.individualId, 10);
            if (relatedIds.includes(indivId)) {
                item.style.display = 'none';
            } else {
                item.style.display = 'flex';
            }
        });
    }

    // Handle dragstart for relationship list items (for removal)
    function handleRelationshipDragStart(e) {
        const relationshipId = e.target.dataset.relationshipId;
        e.dataTransfer.setData('application/x-relationship-id', relationshipId);
        e.dataTransfer.effectAllowed = 'move';
    }

    // Handle dragover and drop on bottom dropzones (for adding relationships)
    bottomDropzones.forEach(dropzone => {
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dropzone-hover');
            e.dataTransfer.dropEffect = 'move';
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dropzone-hover');
        });

        dropzone.addEventListener('drop', async (e) => {
            e.preventDefault();
            dropzone.classList.remove('dropzone-hover');

            const relationshipType = dropzone.dataset.relationshipType;
            const draggedIndividualId = e.dataTransfer.getData('text/plain');

            if (!draggedIndividualId) {
                console.error('Dragged individual ID is missing.');
                alert('An error occurred. Please try again.');
                return;
            }

            const parsedDraggedId = parseInt(draggedIndividualId, 10);
            const parsedTargetId = parseInt(individualId, 10);

            if (isNaN(parsedDraggedId) || isNaN(parsedTargetId)) {
                console.error('Invalid IDs:', { draggedIndividualId, individualId });
                alert('Invalid IDs. Please try again.');
                return;
            }

            // Determine individual_id and related_id based on relationship type
            let individual_id, related_id;
            if (relationshipType === FamilyRelationshipEnum.PARENT) {
                individual_id = parsedDraggedId; // Parent
                related_id = parsedTargetId;     // Child
            } else if (relationshipType === FamilyRelationshipEnum.CHILD) {
                individual_id = parsedTargetId; // Parent
                related_id = parsedDraggedId;   // Child
            } else if (relationshipType === FamilyRelationshipEnum.PARTNER) {
                individual_id = parsedTargetId; // Partner1
                related_id = parsedDraggedId;   // Partner2
            } else {
                console.error('Unknown relationship type:', relationshipType);
                alert('Unknown relationship type. Please contact support.');
                return;
            }

            // Create relationship via API
            try {
                const response = await fetch(`/api/relationships/?project_id=${encodeURIComponent(projectId)}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        individual_id: individual_id,
                        related_id: related_id,
                        relationship_type: relationshipType
                    })
                });

                if (response.ok) {
                    const responseData = await response.json();
                    alert('Relationship created successfully!');
                    // Refresh relationships
                    await fetchAndRenderRelationships();
                } else {
                    const errorData = await response.json();
                    console.error('Error creating relationship:', errorData);
                    alert(errorData.error || 'An error occurred. Please try again.');
                }
            } catch (error) {
                console.error('Error in creating relationship:', error);
                alert('An unexpected error occurred. Please try again.');
            }
        });
    });

    // Handle drop on individuals list (for removing relationships)
    individualsList.addEventListener('dragover', (e) => {
        e.preventDefault();
        individualsList.classList.add('dropzone-hover');
        e.dataTransfer.dropEffect = 'move';
    });

    individualsList.addEventListener('dragleave', () => {
        individualsList.classList.remove('dropzone-hover');
    });

    individualsList.addEventListener('drop', async (e) => {
        e.preventDefault();
        individualsList.classList.remove('dropzone-hover');

        const relationshipId = e.dataTransfer.getData('application/x-relationship-id');

        if (!relationshipId) {
            // Not a relationship item being dragged
            return;
        }

        // Confirm deletion
        if (!confirm('Are you sure you want to remove this relationship?')) {
            return;
        }

        // Delete relationship via API
        try {
            const response = await fetch(`/api/relationships/${encodeURIComponent(relationshipId)}?project_id=${encodeURIComponent(projectId)}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                alert('Relationship removed successfully!');
                // Refresh relationships
                await fetchAndRenderRelationships();
            } else {
                const errorData = await response.json();
                console.error('Error removing relationship:', errorData);
                alert(errorData.error || 'An error occurred. Please try again.');
            }
        } catch (error) {
            console.error('Error in removing relationship:', error);
            alert('An unexpected error occurred. Please try again.');
        }
    });

    // Initialize draggable functionality for Individuals list
    function initializeIndividualsDrag() {
        const individualItems = individualsList.querySelectorAll('li.list-group-item');
        individualItems.forEach(item => {
            item.addEventListener('dragstart', (e) => {
                const individualId = item.dataset.individualId;
                e.dataTransfer.setData('text/plain', individualId);
                e.dataTransfer.effectAllowed = 'move';
            });
        });
    }

    // Initialize draggable functionality for relationship list items
    function initializeRelationshipDrag() {
        const relationshipItems = document.querySelectorAll('ul.list-group li.list-group-item[draggable="true"]');
        relationshipItems.forEach(item => {
            item.addEventListener('dragstart', handleRelationshipDragStart);
        });
    }

    // Fetch and render relationships on page load if individualId is present
    if (individualId && projectId) {
        fetchAndRenderRelationships();
    }

    // Re-initialize drag events after relationships are rendered
    // MutationObserver can be used to detect changes in the relationship lists
    const observerConfig = { childList: true, subtree: true };
    const observerCallback = function(mutationsList, observer) {
        initializeIndividualsDrag();
        initializeRelationshipDrag();
    };
    const observer = new MutationObserver(observerCallback);
    if (parentsList) observer.observe(parentsList, observerConfig);
    if (partnersList) observer.observe(partnersList, observerConfig);
    if (childrenList) observer.observe(childrenList, observerConfig);

    // Initial initialization
    initializeIndividualsDrag();
    initializeRelationshipDrag();
});
