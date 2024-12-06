import { setupIndividualSearch } from './common.js';

document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const individualsList = document.getElementById('individualsList');
    const listItems = Array.from(individualsList.getElementsByClassName('list-group-item'));
    const searchSuggestions = document.getElementById('searchSuggestions');

    // Set up search suggestions with input and suggestion container for the list page
    if (searchInput && searchSuggestions) {
        setupIndividualSearch({
            inputSelector: '#searchInput',
            suggestionsContainerSelector: '#searchSuggestions',
            excludeId: null,
            minQueryLength: 2,
            onSelect: function (individual) {
                // Update the search input with the selected individual's name
                searchInput.value = individual.name;
                searchSuggestions.innerHTML = '';

                // Filter the list based on the selected individual's name
                filterIndividualsList(individual.name.toLowerCase());
            }
        });
    }

    if (searchInput) {
        // Add input event listener for filtering the individual list
        searchInput.addEventListener('input', function () {
            const query = searchInput.value.trim().toLowerCase();

            // Filter individuals based on search query
            filterIndividualsList(query);
        });
    }

    // Function to filter the individuals list based on a query
    function filterIndividualsList(query) {
        listItems.forEach((item) => {
            const itemText = item.textContent.toLowerCase();
            if (itemText.includes(query)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }

    // Hide suggestions when clicking outside of search input or suggestions list
    document.addEventListener('click', function (event) {
        if (searchInput && searchSuggestions) {
            if (!searchInput.contains(event.target) && !searchSuggestions.contains(event.target)) {
                searchSuggestions.innerHTML = '';
            }
        }
    });
});
