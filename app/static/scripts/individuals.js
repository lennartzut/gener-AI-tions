document.addEventListener('DOMContentLoaded', function () {
    const projectPage = document.getElementById('projectPage');
    let projectId = projectPage ? projectPage.dataset.projectId : null;
    const selectedIndividualId = projectPage ? projectPage.dataset.individualId : null;

    const searchInput = document.getElementById('searchInput');
    const searchForm = document.getElementById('searchForm');
    const individualsList = document.getElementById('leftIndividualsList');
    const createIndividualForm = document.getElementById('createIndividualForm');

    let selectMode = false; // optional if you have a "selection" feature
    let excludeIds = [];
    if (selectedIndividualId) {
        excludeIds.push(parseInt(selectedIndividualId, 10));
    }
    let currentQuery = '';

    /**
     * Fetch and render the list of individuals in the left column
     */
    async function fetchAndRenderIndividuals(query = '') {
        currentQuery = query;
        if (!projectId) return;

        const url = `/api/individuals/search?q=${encodeURIComponent(query)}&project_id=${projectId}&exclude_ids=${excludeIds.join(',')}`;

        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                // Ensure JWT cookies are included
                credentials: 'include'
            });
            if (!response.ok) {
                console.error('Fetch Error:', response.status, response.statusText);
                if (response.status === 401) {
                    alert('Session expired or unauthorized. Please log in again.');
                    window.location.href = '/login';
                    return;
                }
                throw new Error(`Failed to fetch individuals. Status ${response.status}.`);
            }

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

                // Determine name
                let name = 'Unknown Name';
                if (individual.primary_identity && individual.primary_identity.first_name) {
                    name = `${individual.primary_identity.first_name} ${individual.primary_identity.last_name || ''}`.trim();
                }

                // Display name
                const nameSpan = document.createElement('span');
                nameSpan.textContent = name;
                nameSpan.classList.add('flex-grow-1');
                item.appendChild(nameSpan);

                // On click: either select or navigate
                item.addEventListener('click', (e) => {
                    if (!selectMode) {
                        // Navigate to individual's detail
                        window.location.href = `/individuals/?project_id=${projectId}&individual_id=${individual.id}`;
                    }
                });

                // Dragstart
                item.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('text/plain', item.dataset.individualId);
                });

                individualsList.appendChild(item);
            });
        } catch (error) {
            console.error('Error fetching individuals:', error);
            alert('An error occurred while fetching individuals.');
        }
    }

    // Initially fetch individuals if the list is present
    if (individualsList) {
        fetchAndRenderIndividuals();
    }

    // Searching
    if (searchForm && searchInput) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            fetchAndRenderIndividuals(searchInput.value.trim());
        });
        searchInput.addEventListener('input', () => {
            fetchAndRenderIndividuals(searchInput.value.trim());
        });
    }

    // Handle Creating an Individual
    if (createIndividualForm) {
        createIndividualForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const formData = new FormData(createIndividualForm);
            const individualData = {
                first_name: formData.get('first_name'),
                last_name: formData.get('last_name'),
                gender: formData.get('gender'),
                birth_date: formData.get('birth_date') || null,
                death_date: formData.get('death_date') || null,
                birth_place: formData.get('birth_place') || null,
                death_place: formData.get('death_place') || null,
                notes: formData.get('notes') || null
            };

            // Convert empty strings to null
            for (const key in individualData) {
                if (individualData[key] === '') {
                    individualData[key] = null;
                }
            }

            try {
                const response = await fetch(`/api/individuals/?project_id=${projectId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify(individualData)
                });

                if (!response.ok) {
                    console.error('Create Individual Error:', response.status, response.statusText);
                    if (response.status === 401) {
                        alert('Session expired or unauthorized. Please log in again.');
                        window.location.href = '/login';
                        return;
                    }
                    const errorData = await response.json();
                    if (errorData.details) {
                        let errorMessages = errorData.details.map(detail =>
                            `${detail.loc.join(' -> ')}: ${detail.msg}`
                        ).join('\n');
                        alert(`Validation Error:\n${errorMessages}`);
                    } else {
                        alert(errorData.error || 'Failed to create individual.');
                    }
                    return;
                }

                // Success
                alert('Individual created successfully!');
                createIndividualForm.reset();

                // Hide the modal
                const createModalEl = document.getElementById('createIndividualModal');
                const createModal = bootstrap.Modal.getInstance(createModalEl);
                if (createModal) {
                    createModal.hide();
                }

                // Re-fetch individuals
                fetchAndRenderIndividuals(currentQuery);

            } catch (error) {
                console.error('Error creating individual:', error);
                alert('An unexpected error occurred.');
            }
        });
    }
});