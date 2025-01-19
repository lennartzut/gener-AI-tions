// Enums for relationship details
const verticalEnum = ['biological', 'step', 'adoptive', 'foster', 'other'];
const horizontalEnum = ['marriage', 'civil union', 'partnership'];

document.addEventListener('DOMContentLoaded', () => {
    const projectPage = document.getElementById('projectPage');
    if (!projectPage) return;

    const projectId = projectPage.dataset.projectId;
    const individualId = projectPage.dataset.individualId;

    // Right side lists
    const parentsList = document.getElementById('parentsList');
    const partnersList = document.getElementById('partnersList');
    const childrenList = document.getElementById('childrenList');
    const siblingsList = document.getElementById('siblingsList');

    // Left side list
    const leftIndividualsList = document.getElementById('leftIndividualsList');

    /**
     * Fetch all individuals and populate the left column
     */
    async function fetchAllIndividuals() {
        try {
            const response = await fetch(`/api/individuals/?project_id=${projectId}`, {
                method: 'GET',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                throw new Error(`Failed to fetch individuals. Status: ${response.status}`);
            }

            const data = await response.json();
            const individuals = data.individuals || [];

            // Clear existing list
            leftIndividualsList.innerHTML = '';

            if (individuals.length === 0) {
                leftIndividualsList.innerHTML = '<li class="list-group-item text-muted">No individuals found.</li>';
                return;
            }

            individuals.forEach(ind => {
                const li = document.createElement('li');
                li.className = 'list-group-item d-flex align-items-center';
                li.setAttribute('draggable', 'true');
                li.style.cursor = 'pointer';
                li.dataset.individualId = ind.id;

                // Display name
                let displayName = 'Unknown';
                if (ind.primary_identity && ind.primary_identity.first_name) {
                    displayName = `${ind.primary_identity.first_name} ${ind.primary_identity.last_name || ''}`.trim();
                }
                li.textContent = displayName;

                // Click event to select individual
                li.addEventListener('click', () => {
                    window.location.href = `/individuals/?project_id=${projectId}&individual_id=${ind.id}`;
                });

                // Drag event to create relationship
                li.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('text/plain', ind.id);
                    e.dataTransfer.effectAllowed = 'move';
                });

                leftIndividualsList.appendChild(li);
            });
        } catch (error) {
            console.error('Error fetching individuals:', error);
            alert('Failed to load individuals.');
        }
    }

    /**
     * Fetch selected individual's relationships and populate the right column
     */
    async function fetchAndRenderRelationships() {
        if (!individualId) return;

        try {
            const response = await fetch(`/api/individuals/${individualId}?project_id=${projectId}`, {
                method: 'GET',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                throw new Error(`Failed to fetch relationships. Status: ${response.status}`);
            }

            const data = await response.json();
            const indData = data.data;

            // Render each relationship list
            renderRelList(parentsList, indData.parents, 'parent');
            renderRelList(partnersList, indData.partners, 'partner');
            renderRelList(childrenList, indData.children, 'child');
            renderSiblingsList(indData.siblings);

            // Exclude related individuals from the left column
            excludeRelatedOnLeft(indData);
        } catch (error) {
            console.error('Error fetching relationships:', error);
            alert('Failed to load relationships.');
        }
    }

    /**
     * Render a list of relationships (parents, partners, children)
     */
    function renderRelList(ul, relArray, relType) {
        ul.innerHTML = '';

        if (!relArray || relArray.length === 0) {
            ul.innerHTML = `<li class="list-group-item text-muted">No ${relType}s assigned.</li>`;
            return;
        }

        relArray.forEach(rel => {
            const li = document.createElement('li');
            li.className = 'list-group-item d-flex flex-column';
            li.draggable = true;
            li.dataset.relationshipId = rel.relationship_id;
            li.dataset.individualId = rel.id;
            li.dataset.relationshipType = relType;

            // Top row with name and "Show Details" button
            const topRow = document.createElement('div');
            topRow.className = 'd-flex justify-content-between align-items-center';

            // Name span
            const nameSpan = document.createElement('span');
            const firstName = rel.first_name || 'Unknown';
            const lastName = rel.last_name || '';
            nameSpan.textContent = `${firstName} ${lastName}`.trim();

            // Show Details button
            const detailsBtn = document.createElement('button');
            detailsBtn.className = 'btn btn-sm btn-outline-secondary show-details-btn';
            detailsBtn.textContent = 'Show Details';
            detailsBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                toggleRelDetails(li, rel, relType);
            });

            topRow.appendChild(nameSpan);
            topRow.appendChild(detailsBtn);
            li.appendChild(topRow);

            // Drag event for relationships
            li.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('application/x-relationship-id', rel.relationship_id);
                e.dataTransfer.setData('text/plain', rel.id);
                e.dataTransfer.effectAllowed = 'move';
            });

            // Click event to navigate to individual
            li.addEventListener('click', () => {
                window.location.href = `/individuals/?project_id=${projectId}&individual_id=${rel.id}`;
            });

            ul.appendChild(li);
        });
    }

    /**
     * Render the siblings list
     */
    function renderSiblingsList(siblings) {
        siblingsList.innerHTML = '';

        if (!siblings || siblings.length === 0) {
            siblingsList.innerHTML = '<li class="list-group-item text-muted">No siblings assigned.</li>';
            return;
        }

        siblings.forEach(sib => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            const firstName = sib.first_name || 'Unknown';
            const lastName = sib.last_name || '';
            li.textContent = `${firstName} ${lastName} (ID: ${sib.id})`;
            li.style.cursor = 'pointer';

            // Click event to navigate to sibling's page
            li.addEventListener('click', () => {
                window.location.href = `/individuals/?project_id=${projectId}&individual_id=${sib.id}`;
            });

            siblingsList.appendChild(li);
        });
    }

    /**
     * Exclude related individuals from the left column
     */
    function excludeRelatedOnLeft(indData) {
        const usedIds = new Set();

        // Exclude the selected individual
        const selectedId = parseInt(indData.id, 10);
        usedIds.add(selectedId);

        // Add parents, partners, and children to usedIds
        [...(indData.parents || []), ...(indData.partners || []), ...(indData.children || [])]
            .forEach(rel => usedIds.add(parseInt(rel.id, 10)));

        // Hide used individuals in the left list
        const items = leftIndividualsList.querySelectorAll('li.list-group-item');
        items.forEach(item => {
            const indivId = parseInt(item.dataset.individualId, 10);
            if (usedIds.has(indivId)) {
                item.style.display = 'none';
            } else {
                item.style.display = 'flex'; // or 'list-item'
            }
        });
    }

    /**
     * Handle drag-and-drop for creating relationships
     */
    [parentsList, partnersList, childrenList].forEach(ul => {
        ul.addEventListener('dragover', (e) => {
            e.preventDefault();
        });

        ul.addEventListener('drop', async (e) => {
            e.preventDefault();

            if (!individualId) return;

            const existingRelId = e.dataTransfer.getData('application/x-relationship-id');
            const draggedIndId = parseInt(e.dataTransfer.getData('text/plain'), 10);
            const newRelType = ul.dataset.relationshipType;

            if (existingRelId) {
                // Update existing relationship
                await updateExistingRelationship(existingRelId, newRelType);
            } else {
                // Create new relationship
                await createRelationship(newRelType, draggedIndId);
            }
        });
    });

    /**
     * Handle dropping onto the left column to remove relationships
     */
    leftIndividualsList.addEventListener('dragover', (e) => {
        e.preventDefault();
    });

    leftIndividualsList.addEventListener('drop', async (e) => {
        e.preventDefault();

        const relId = e.dataTransfer.getData('application/x-relationship-id');
        if (!relId) return;

        await removeRelationship(relId);
    });

    /**
     * Create a new relationship
     */
    async function createRelationship(relType, draggedId) {
        if (!individualId) return;

        const selectedId = parseInt(individualId, 10);

        let indiv_id, rel_id, detail;
        if (relType === 'child') {
            // Selected is the parent
            indiv_id = selectedId;
            rel_id = draggedId;
            relType = 'parent'; // Store as 'parent' in DB
            detail = 'biological';
        } else if (relType === 'parent') {
            // Dragged is the parent
            indiv_id = draggedId;
            rel_id = selectedId;
            detail = 'biological';
        } else if (relType === 'partner') {
            indiv_id = selectedId;
            rel_id = draggedId;
            detail = 'marriage';
        } else {
            alert(`Unknown relationship type: ${relType}`);
            return;
        }

        const payload = {
            individual_id: indiv_id,
            related_id: rel_id,
            initial_relationship: relType,
            relationship_detail: detail
        };

        try {
            const response = await fetch(`/api/relationships/?project_id=${projectId}`, {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errData = await response.json();
                alert(errData.error || 'Failed to create relationship.');
                return;
            }

            alert('Relationship created successfully!');

            // Re-fetch and re-render lists
            await fetchAllIndividuals();
            await fetchAndRenderRelationships();

        } catch (error) {
            console.error('Error creating relationship:', error);
            alert('An error occurred while creating the relationship.');
        }
    }

    /**
     * Update an existing relationship
     */
    async function updateExistingRelationship(relId, newRelType) {
        let initial_relationship, relationship_detail;

        if (newRelType === 'child') {
            initial_relationship = 'parent';
            relationship_detail = 'biological';
        } else if (newRelType === 'parent') {
            initial_relationship = 'parent';
            relationship_detail = 'biological';
        } else if (newRelType === 'partner') {
            initial_relationship = 'partner';
            relationship_detail = 'marriage';
        } else {
            alert(`Unknown relationship type: ${newRelType}`);
            return;
        }

        try {
            const response = await fetch(`/api/relationships/${relId}?project_id=${projectId}`, {
                method: 'PATCH',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ initial_relationship, relationship_detail })
            });

            if (!response.ok) {
                const errData = await response.json();
                alert(errData.error || 'Failed to update relationship.');
                return;
            }

            alert('Relationship updated successfully!');
            await fetchAllIndividuals();
            await fetchAndRenderRelationships();

        } catch (error) {
            console.error('Error updating relationship:', error);
            alert('An error occurred while updating the relationship.');
        }
    }

    /**
     * Remove an existing relationship
     */
    async function removeRelationship(relId) {
        try {
            const response = await fetch(`/api/relationships/${relId}?project_id=${projectId}`, {
                method: 'DELETE',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                const errData = await response.json();
                alert(errData.error || 'Failed to delete relationship.');
                return;
            }

            alert('Relationship deleted successfully.');

            // Re-fetch and re-render lists
            await fetchAllIndividuals();
            await fetchAndRenderRelationships();

        } catch (error) {
            console.error('Error removing relationship:', error);
            alert('An error occurred while removing the relationship.');
        }
    }

    /**
     * Patch (update) a relationship
     */
    async function patchRelationship(relId, updates) {
        try {
            const response = await fetch(`/api/relationships/${relId}?project_id=${projectId}`, {
                method: 'PATCH',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updates)
            });

            if (!response.ok) {
                const msg = await response.json();
                alert(msg.error || 'Failed to update relationship.');
                return;
            }

            alert('Relationship updated successfully!');
            await fetchAllIndividuals();
            await fetchAndRenderRelationships();

        } catch (error) {
            console.error('Error patching relationship:', error);
            alert('An error occurred while updating the relationship.');
        }
    }

    /**
     * Toggle relationship details display
     */
    async function toggleRelDetails(li, rel, relationshipType) {
        const existing = li.querySelector('.rel-details-collapse');
        if (existing) {
            existing.remove();
            return;
        }

        const detailsDiv = document.createElement('div');
        detailsDiv.className = 'rel-details-collapse mt-2 p-2 border';

        let dateFields = '';
        if (relationshipType === 'partner') {
            const uDate = rel.union_date || '';
            const dDate = rel.dissolution_date || '';
            dateFields = `
                <div class="mb-3">
                    <label class="form-label">Union Date</label>
                    <input type="date" class="form-control" name="union_date" value="${uDate}">
                </div>
                <div class="mb-3">
                    <label class="form-label">Dissolution Date</label>
                    <input type="date" class="form-control" name="dissolution_date" value="${dDate}">
                </div>
            `;
        }

        const isPartner = (relationshipType === 'partner');
        const enumOptions = isPartner ? horizontalEnum : verticalEnum;
        const relDetail = rel.relationship_detail || '';
        let detailSelect = `
            <label class="form-label">Relationship Detail</label>
            <select name="relationship_detail" class="form-select mb-3">
        `;
        enumOptions.forEach(opt => {
            // Removed 'selected' attribute to avoid conflicts
            detailSelect += `<option value="${opt}">${opt}</option>`;
        });
        detailSelect += '</select>';

        const notesVal = rel.notes || '';
        const notesField = `
            <label class="form-label">Notes</label>
            <textarea class="form-control mb-3" name="notes" rows="2">${notesVal}</textarea>
        `;

        detailsDiv.innerHTML = `
            ${detailSelect}
            ${dateFields}
            ${notesField}
            <button class="btn btn-sm btn-primary me-2">Save</button>
            <button class="btn btn-sm btn-secondary" type="button">Cancel</button>
        `;
        li.appendChild(detailsDiv);

        // **Enhancement 1: Display Current relationship_detail**
        const selectElement = detailsDiv.querySelector('[name="relationship_detail"]');
        if (selectElement) {
            if (enumOptions.includes(relDetail)) {
                selectElement.value = relDetail;
            } else if (relDetail) {
                // Add the current relDetail as an option if it's not in enumOptions
                const option = document.createElement('option');
                option.value = relDetail;
                option.text = relDetail;
                option.selected = true;
                selectElement.appendChild(option);
            } else {
                // If relDetail is empty or undefined, optionally set a default value
                selectElement.value = ''; // Or set to a default like 'other'
            }
        }

        // **Enhancement 2: Prevent Clicks on Form Elements from Selecting the Related Individual**
        const formElements = detailsDiv.querySelectorAll('input, select, textarea, button');
        formElements.forEach(elem => {
            elem.addEventListener('click', (e) => {
                e.stopPropagation();
            });
            elem.addEventListener('focus', (e) => {
                e.stopPropagation();
            });
        });

        const saveBtn = detailsDiv.querySelector('.btn-primary');
        const cancelBtn = detailsDiv.querySelector('.btn-secondary');

        saveBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            const relationship_detail = detailsDiv.querySelector('[name="relationship_detail"]').value;
            const notes = detailsDiv.querySelector('[name="notes"]').value;
            let union_date = null, dissolution_date = null;
            if (relationshipType === 'partner') {
                union_date = detailsDiv.querySelector('[name="union_date"]').value || null;
                dissolution_date = detailsDiv.querySelector('[name="dissolution_date"]').value || null;
            }
            await patchRelationship(rel.relationship_id, { relationship_detail, union_date, dissolution_date, notes });
            detailsDiv.remove();
        });

        cancelBtn.addEventListener('click', () => {
            detailsDiv.remove();
        });
    }

    /**
     * Initialize the page by fetching all individuals and relationships
     */
    async function init() {
        await fetchAllIndividuals();
        if (individualId) {
            await fetchAndRenderRelationships();
        }
    }

    init();
});