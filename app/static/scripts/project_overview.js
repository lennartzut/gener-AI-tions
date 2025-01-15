const InitialRelationshipEnum = {
    CHILD: 'child',
    PARENT: 'parent',
    PARTNER: 'partner'
};

const HorizontalRelationshipTypeEnum = {
    BIOLOGICAL: 'biological',
    STEP: 'step',
    ADOPTIVE: 'adoptive',
    FOSTER: 'foster',
    OTHER: 'other'
};

const VerticalRelationshipTypeEnum = {
    MARRIAGE: 'marriage',
    CIVIL_UNION: 'civil union',
    PARTNERSHIP: 'partnership'
};

document.addEventListener('DOMContentLoaded', function () {
    const projectPage = document.getElementById('projectPage');
    if (!projectPage) return;

    const projectId = projectPage.dataset.projectId;
    const individualId = projectPage.dataset.individualId;

    const bottomDropzones = document.querySelectorAll('.d-flex.justify-content-around .dropzone');
    const parentsList = document.getElementById('parentsList');
    const partnersList = document.getElementById('partnersList');
    const childrenList = document.getElementById('childrenList');
    const verticalList = document.getElementById('verticalList');

    async function fetchAndRenderRelationships() {
        if (!individualId) return;

        try {
            const response = await fetch(`/api/relationships/individual/${individualId}?project_id=${encodeURIComponent(projectId)}`, {
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) throw new Error('Failed to fetch relationships');

            const data = await response.json();
            const relationships = data.relationships;

            populateRelationshipList(parentsList, relationships.parents, InitialRelationshipEnum.PARENT);
            populateRelationshipList(partnersList, relationships.partners, InitialRelationshipEnum.PARTNER);
            populateRelationshipList(childrenList, relationships.children, InitialRelationshipEnum.CHILD);
            populateRelationshipList(verticalList, relationships.vertical, 'Vertical Relationship');

            excludeRelatedIndividuals(relationships);
        } catch (error) {
            console.error('Error fetching relationships:', error);
        }
    }

    function populateRelationshipList(listElement, relationships, relationshipType) {
        listElement.innerHTML = '';

        if (relationships.length > 0) {
            relationships.forEach(rel => {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
                listItem.setAttribute('draggable', 'true');
                listItem.dataset.relationshipId = rel.relationship_id;
                listItem.dataset.individualId = rel.id;

                listItem.innerHTML = `
                    <span>${rel.first_name || 'Unknown'} ${rel.last_name || ''}</span>
                    <small class="text-muted">ID: ${rel.id} (${relationshipType})</small>
                `;

                listItem.addEventListener('dragstart', handleRelationshipDragStart);
                listElement.appendChild(listItem);
            });
        } else {
            listElement.innerHTML = `<li class="list-group-item text-muted">No ${relationshipType}s assigned.</li>`;
        }
    }

    function excludeRelatedIndividuals(relationships) {
        const relatedIds = [
            ...relationships.parents.map(rel => rel.id),
            ...relationships.partners.map(rel => rel.id),
            ...relationships.children.map(rel => rel.id),
            ...relationships.vertical.map(rel => rel.id)
        ];

        const individualItems = document.querySelectorAll('#leftIndividualsList li.list-group-item');
        individualItems.forEach(item => {
            const indivId = parseInt(item.dataset.individualId, 10);
            item.style.display = relatedIds.includes(indivId) ? 'none' : 'flex';
        });
    }

    function handleRelationshipDragStart(e) {
        const relationshipId = e.target.dataset.relationshipId;
        e.dataTransfer.setData('application/x-relationship-id', relationshipId);
        e.dataTransfer.effectAllowed = 'move';
    }

    bottomDropzones.forEach(dropzone => {
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dropzone-hover');
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
                alert('An error occurred. Please try again.');
                return;
            }

            let individual_id, related_id;
            if (relationshipType === InitialRelationshipEnum.PARENT) {
                individual_id = parseInt(draggedIndividualId, 10);
                related_id = parseInt(individualId, 10);
            } else if (relationshipType === InitialRelationshipEnum.CHILD) {
                individual_id = parseInt(individualId, 10);
                related_id = parseInt(draggedIndividualId, 10);
            } else if (relationshipType === InitialRelationshipEnum.PARTNER || relationshipType === VerticalRelationshipTypeEnum.MARRIAGE) {
                individual_id = parseInt(individualId, 10);
                related_id = parseInt(draggedIndividualId, 10);
            } else {
                alert('Unknown relationship type.');
                return;
            }

            try {
                const response = await fetch(`/api/relationships/?project_id=${projectId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        individual_id: individual_id,
                        related_id: related_id,
                        initial_relationship: relationshipType,
                        relationship_detail: HorizontalRelationshipTypeEnum.BIOLOGICAL
                    })
                });

                if (response.ok) {
                    alert('Relationship created successfully!');
                    fetchAndRenderRelationships();
                } else {
                    const errorData = await response.json();
                    alert(errorData.error || 'Failed to create relationship.');
                }
            } catch (error) {
                console.error('Error creating relationship:', error);
                alert('An unexpected error occurred.');
            }
        });
    });

    if (individualId) fetchAndRenderRelationships();
});
