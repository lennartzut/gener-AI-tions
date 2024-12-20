import { toggleDeathFields } from './common.js';

document.addEventListener('DOMContentLoaded', function () {
    const projectPage = document.getElementById('projectPage');
    const projectId = projectPage ? projectPage.dataset.projectId : null;
    const selectedIndividualId = projectPage ? projectPage.dataset.individualId : null;

    const searchInput = document.getElementById('searchInput');
    const searchForm = document.getElementById('searchForm');
    const individualsList = document.getElementById('leftIndividualsList');
    const selectModeButton = document.getElementById('selectModeButton');
    const deleteSelectedButton = document.getElementById('deleteSelectedButton');

    let selectMode = false;
    let excludeIds = selectedIndividualId ? [parseInt(selectedIndividualId)] : [];
    let currentQuery = ''; // Current search query

    async function fetchAndRenderIndividuals(query = '') {
        currentQuery = query;
        const projectParam = projectId ? `&project_id=${encodeURIComponent(projectId)}` : '';
        const allExcludeIds = excludeIds.join(',');
        const excludeParam = allExcludeIds ? `&exclude_ids=${allExcludeIds}` : '';
        const url = `/api/individuals/search?q=${encodeURIComponent(query)}${projectParam}${excludeParam}`;

        try {
            const response = await fetch(url, {
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch individuals');
            }

            const data = await response.json();
            individualsList.innerHTML = '';

            if (!data.individuals || data.individuals.length === 0) {
                const noResultItem = document.createElement('li');
                noResultItem.className = 'list-group-item text-muted';
                noResultItem.textContent = 'No individuals found.';
                individualsList.appendChild(noResultItem);
                return;
            }

            // Check duplicates
            const nameCount = {};
            data.individuals.forEach(ind => {
                nameCount[ind.name] = (nameCount[ind.name] || 0) + 1;
            });
            for (let name in nameCount) {
                if (nameCount[name] > 1) {
                    if (confirm(`Found duplicates for "${name}". Merge them?`)) {
                        console.log(`Merging duplicates of ${name}...`);
                        // Implement merging as needed
                    }
                }
            }

            data.individuals.forEach((individual) => {
                const item = document.createElement('li');
                item.className = 'list-group-item d-flex align-items-center';
                item.setAttribute('draggable', 'true');
                item.dataset.individualId = individual.id;

                if (selectMode) {
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.classList.add('form-check-input', 'me-2');
                    checkbox.value = individual.id;
                    item.appendChild(checkbox);
                }

                const nameSpan = document.createElement('span');
                nameSpan.textContent = individual.name;
                nameSpan.classList.add('flex-grow-1');
                item.appendChild(nameSpan);

                item.addEventListener('click', (e) => {
                    if (selectMode && e.target.type === 'checkbox') return;
                    if (!selectMode) {
                        // Navigate to this individual, keeping project_id and individual_id
                        window.location.href = `/individuals/?project_id=${projectId}&individual_id=${individual.id}`;
                    }
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

    // Initial load: fetch full list with no query
    if (individualsList) {
        fetchAndRenderIndividuals('');
    }

    // Handle search form submit (pressing Enter in the search field)
    if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const q = searchInput.value.trim();
            fetchAndRenderIndividuals(q);
        });
    }

    // On input changes, fetch on the fly for real-time updates
    if (searchInput && individualsList) {
        searchInput.addEventListener('input', function () {
            const q = searchInput.value.trim();
            fetchAndRenderIndividuals(q);
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
            const checkboxes = individualsList.querySelectorAll('input[type="checkbox"]:checked');
            const idsToDelete = Array.from(checkboxes).map(cb => parseInt(cb.value, 10));

            for (let id of idsToDelete) {
                try {
                    const projectParam = projectId ? `?project_id=${encodeURIComponent(projectId)}` : '';
                    const response = await fetch(`/api/individuals/${id}${projectParam}`, {
                        method: 'DELETE'
                    });
                    if (!response.ok) {
                        console.error(`Failed to delete individual ${id}`);
                    }
                } catch (err) {
                    console.error(`Error deleting individual ${id}:`, err);
                }
            }

            fetchAndRenderIndividuals(currentQuery);
        });
    }

    // Create Individual Form handling
    const createIndividualForm = document.getElementById('createIndividualForm');
    if (createIndividualForm) {
        toggleDeathFields();

        const isDeceasedCheckbox = document.getElementById('isDeceased');
        const isDeceasedUnknownCheckbox = document.getElementById('isDeceasedUnknown');

        if (isDeceasedCheckbox) {
            isDeceasedCheckbox.addEventListener('change', () => {
                if (isDeceasedUnknownCheckbox && isDeceasedUnknownCheckbox.checked) {
                    isDeceasedUnknownCheckbox.checked = false;
                }
                toggleDeathFields();
            });
        }

        if (isDeceasedUnknownCheckbox) {
            isDeceasedUnknownCheckbox.addEventListener('change', () => {
                if (isDeceasedCheckbox && isDeceasedCheckbox.checked) {
                    isDeceasedCheckbox.checked = false;
                }
                toggleDeathFields();
            });
        }

        createIndividualForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const formData = new FormData(createIndividualForm);
            const projectIdFromForm = formData.get('project_id') || projectId;

            const individualData = {
                birth_date: formData.get('birth_date') || null,
                birth_place: formData.get('birth_place') || null,
                death_date: formData.get('death_date') || null,
                death_place: formData.get('death_place') || null,
                first_name: formData.get('first_name') || null,
                last_name: formData.get('last_name') || null,
                gender: formData.get('gender') || null,
            };

            const isDUC = isDeceasedUnknownCheckbox && isDeceasedUnknownCheckbox.checked;
            if (isDUC) {
                individualData.death_date = null;
                individualData.death_place = null;
            }

            if (!individualData.first_name || !individualData.last_name || !individualData.gender) {
                alert('Please fill out all required fields: First Name, Last Name, and Gender.');
                return;
            }

            const createUrl = `/api/individuals/?project_id=${encodeURIComponent(projectIdFromForm)}`;
            try {
                const response = await fetch(createUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify(individualData),
                });

                if (response.ok) {
                    alert('Individual created successfully!');
                    fetchAndRenderIndividuals(currentQuery);
                } else {
                    const data = await response.json();
                    console.error('Error creating individual:', data);
                    alert(data.error || 'An error occurred. Please try again.');
                }
            } catch (error) {
                console.error('Error creating individual:', error);
                alert('An unexpected error occurred. Please try again.');
            }
        });
    }

    // Add Identity Modal
    const addIdentityBtn = document.getElementById('addIdentityBtn');
    const addIdentityModal = document.getElementById('addIdentityModal');
    if (addIdentityBtn && addIdentityModal && selectedIndividualId) {
        addIdentityBtn.addEventListener('click', () => {
            const modal = new bootstrap.Modal(addIdentityModal);
            modal.show();
        });
    }
});
