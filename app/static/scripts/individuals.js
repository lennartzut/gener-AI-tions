// File: static/scripts/individuals.js

document.addEventListener('DOMContentLoaded', function () {
    const projectPage = document.getElementById('projectPage');
    let projectId = projectPage ? projectPage.dataset.projectId : null;
    const selectedIndividualId = projectPage ? projectPage.dataset.individualId : null;

    const searchInput = document.getElementById('searchInput');
    const searchForm = document.getElementById('searchForm');
    const individualsList = document.getElementById('leftIndividualsList');
    const selectModeButton = document.getElementById('selectModeButton');
    const deleteSelectedButton = document.getElementById('deleteSelectedButton');
    const createIndividualForm = document.getElementById('createIndividualForm');

    let projectIdInputInModal = createIndividualForm?.querySelector('#modalProjectId');
    if (!projectId && projectIdInputInModal?.value) {
        projectId = projectIdInputInModal.value;
    }

    let selectMode = false;
    let excludeIds = [];
    if (selectedIndividualId) {
        excludeIds.push(parseInt(selectedIndividualId, 10));
    }
    let currentQuery = '';

    async function fetchAndRenderIndividuals(query = '') {
        currentQuery = query;
        if (!projectId) return;

        const url = `/api/individuals/search?q=${encodeURIComponent(query)}&project_id=${projectId}&exclude_ids=${excludeIds.join(',')}`;

        try {
            const response = await fetch(url, { headers: { 'Content-Type': 'application/json' } });
            if (!response.ok) throw new Error('Failed to fetch individuals');

            const data = await response.json();
            individualsList.innerHTML = '';

            if (!data.individuals || data.individuals.length === 0) {
                individualsList.innerHTML = '<li class="list-group-item text-muted">No individuals found.</li>';
                return;
            }

            data.individuals.forEach(individual => {
                const item = document.createElement('li');
                item.className = 'list-group-item d-flex align-items-center';
                item.setAttribute('draggable', 'true');
                item.dataset.individualId = individual.id;

                const nameSpan = document.createElement('span');
                nameSpan.textContent = `${individual.primary_identity?.first_name || 'Unknown'} ${individual.primary_identity?.last_name || 'Name'}`;
                nameSpan.classList.add('flex-grow-1');
                item.appendChild(nameSpan);

                if (selectMode) {
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.value = individual.id;
                    checkbox.classList.add('form-check-input', 'me-2');
                    item.prepend(checkbox);
                }

                item.addEventListener('click', (e) => {
                    if (selectMode && e.target.type === 'checkbox') return;
                    if (!selectMode) window.location.href = `/individuals/?project_id=${projectId}&individual_id=${individual.id}`;
                });

                item.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('text/plain', item.dataset.individualId);
                });

                individualsList.appendChild(item);
            });
        } catch (error) {
            console.error('Error fetching individuals:', error);
        }
    }

    if (individualsList) fetchAndRenderIndividuals();

    if (searchForm && searchInput) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            fetchAndRenderIndividuals(searchInput.value.trim());
        });

        searchInput.addEventListener('input', () => {
            fetchAndRenderIndividuals(searchInput.value.trim());
        });
    }

    if (selectModeButton && deleteSelectedButton) {
        selectModeButton.addEventListener('click', () => {
            selectMode = !selectMode;
            selectModeButton.textContent = selectMode ? 'Cancel' : 'Select';
            deleteSelectedButton.style.display = selectMode ? 'inline-block' : 'none';
            fetchAndRenderIndividuals(currentQuery);
        });

        deleteSelectedButton.addEventListener('click', async () => {
            const selectedIds = Array.from(individualsList.querySelectorAll('input[type="checkbox"]:checked')).map(checkbox => parseInt(checkbox.value, 10));

            for (const id of selectedIds) {
                try {
                    const response = await fetch(`/api/individuals/${id}?project_id=${projectId}`, { method: 'DELETE' });
                    if (!response.ok) throw new Error(`Failed to delete individual ${id}`);
                } catch (error) {
                    console.error(`Error deleting individual ${id}:`, error);
                }
            }

            fetchAndRenderIndividuals(currentQuery);
        });
    }

    if (createIndividualForm) {
        createIndividualForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const formData = new FormData(createIndividualForm);
            const individualData = {
                first_name: formData.get('first_name'),
                last_name: formData.get('last_name'),
                gender: formData.get('gender'),
                birth_date: formData.get('birth_date'),
                death_date: formData.get('death_date'),
                birth_place: formData.get('birth_place'),
                death_place: formData.get('death_place'),
                notes: formData.get('notes')
            };

            try {
                const response = await fetch(`/api/individuals/?project_id=${projectId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(individualData)
                });

                if (response.ok) {
                    alert('Individual created successfully!');
                    fetchAndRenderIndividuals(currentQuery);
                } else {
                    const errorData = await response.json();
                    alert(errorData.error || 'Failed to create individual.');
                }
            } catch (error) {
                console.error('Error creating individual:', error);
                alert('An unexpected error occurred.');
            }
        });
    }
});
