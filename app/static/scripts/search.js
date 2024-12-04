function setupIndividualSearch(options) {
    const {
        inputSelector,
        hiddenInputSelector,
        suggestionsContainerSelector,
        excludeId = null,
        minQueryLength = 2,
        delay = 300,
        onSelect = null
    } = options;

    const targetNameInput = document.querySelector(inputSelector);
    const targetIdInput = hiddenInputSelector ? document.querySelector(hiddenInputSelector) : null;
    const suggestionsBox = document.querySelector(suggestionsContainerSelector);

    if (!targetNameInput || !suggestionsBox) {
        console.error('Search input or suggestions container not found.');
        return;
    }

    let timeout = null;

    targetNameInput.addEventListener('input', function () {
        clearTimeout(timeout);
        const query = this.value.trim();

        if (query.length < minQueryLength) {
            suggestionsBox.innerHTML = '';
            return;
        }

        timeout = setTimeout(async function () {
            try {
                let url = '/api/individuals/search?q=' + encodeURIComponent(query);
                if (excludeId) {
                    url += '&exclude_id=' + excludeId;
                }

                const response = await fetch(url, { credentials: 'include' });
                const data = await response.json();
                suggestionsBox.innerHTML = '';

                data.individuals.forEach(individual => {
                    const suggestionItem = document.createElement('a');
                    suggestionItem.href = '#';
                    suggestionItem.className = 'list-group-item list-group-item-action';
                    suggestionItem.textContent = individual.name;
                    suggestionItem.dataset.id = individual.id;

                    suggestionItem.addEventListener('click', function (e) {
                        e.preventDefault();
                        if (onSelect) {
                            onSelect(individual);
                        } else {
                            targetNameInput.value = individual.name;
                            if (targetIdInput) {
                                targetIdInput.value = individual.id;
                            }
                            suggestionsBox.innerHTML = '';
                        }
                    });

                    suggestionsBox.appendChild(suggestionItem);
                });
            } catch (error) {
                console.error('Error fetching suggestions:', error);
            }
        }, delay);
    });

    // Hide suggestions when clicking outside
    document.addEventListener('click', function (e) {
        if (!targetNameInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.innerHTML = '';
        }
    });
}

window.setupIndividualSearch = setupIndividualSearch;
