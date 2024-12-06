// common.js
export function toggleDeathFields() {
    const isDeceased = document.getElementById('isDeceased')?.checked;
    const isDeceasedUnknown = document.getElementById('isDeceasedUnknown')?.checked;
    const deathFields = document.getElementById('deathFields');

    if (deathFields) {
        deathFields.style.display = (isDeceased && !isDeceasedUnknown) ? 'block' : 'none';
    }
}

export function setupIndividualSearch({
    inputSelector,
    suggestionsContainerSelector,
    excludeId,
    minQueryLength = 2,
    onSelect
}) {
    const input = document.querySelector(inputSelector);
    const suggestionsContainer = document.querySelector(suggestionsContainerSelector);

    if (!input || !suggestionsContainer) {
        console.error('Input or suggestions container not found.');
        return;
    }

    input.addEventListener('input', async function () {
        const query = input.value.trim();

        if (query.length < minQueryLength) {
            suggestionsContainer.innerHTML = '';
            return;
        }

        try {
            const response = await fetch(`/api/individuals/search?q=${encodeURIComponent(query)}&exclude_id=${excludeId || ''}`, {
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch suggestions');
            }

            const data = await response.json();
            suggestionsContainer.innerHTML = '';

            if (data.individuals.length === 0) {
                const noResultItem = document.createElement('div');
                noResultItem.className = 'list-group-item list-group-item-action';
                noResultItem.textContent = 'No results found';
                suggestionsContainer.appendChild(noResultItem);
            } else {
                data.individuals.forEach((individual) => {
                    const item = document.createElement('div');
                    item.className = 'list-group-item list-group-item-action';
                    item.textContent = individual.name;

                    item.addEventListener('click', function () {
                        if (onSelect) {
                            onSelect(individual);
                        }
                    });

                    suggestionsContainer.appendChild(item);
                });
            }
        } catch (error) {
            console.error('Error fetching suggestions:', error);
        }
    });
}
