import { setupIndividualSearch } from './common.js';

document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const searchSuggestions = document.getElementById('searchSuggestions');

    // Setup search for individuals list page
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
            }
        });
    }

    // Set up search for adding parents, partners, or children in the family card
    const familySearchFields = [
        { inputSelector: '#parentName', suggestionsContainerSelector: '#parentSuggestions', hiddenInputId: 'parentId' },
        { inputSelector: '#partnerName', suggestionsContainerSelector: '#partnerSuggestions', hiddenInputId: 'partnerId' },
        { inputSelector: '#childName', suggestionsContainerSelector: '#childSuggestions', hiddenInputId: 'childId' }
    ];

    familySearchFields.forEach(({ inputSelector, suggestionsContainerSelector, hiddenInputId }) => {
        const inputElement = document.querySelector(inputSelector);
        const suggestionsElement = document.querySelector(suggestionsContainerSelector);
        const hiddenInputElement = document.getElementById(hiddenInputId);

        if (inputElement && suggestionsElement && hiddenInputElement) {
            setupIndividualSearch({
                inputSelector,
                suggestionsContainerSelector,
                excludeId: null,
                minQueryLength: 2,
                onSelect: function (individual) {
                    // Update the input with the selected individual's name
                    inputElement.value = individual.name;
                    // Set the hidden field to selected individual's ID
                    hiddenInputElement.value = individual.id;
                    // Clear suggestions once selection is made
                    suggestionsElement.innerHTML = '';
                }
            });
        }
    });

    // Hide suggestions when clicking outside of search input or suggestions list
    document.addEventListener('click', function (event) {
        // Handle individuals list search
        if (searchInput && searchSuggestions) {
            if (!searchInput.contains(event.target) && !searchSuggestions.contains(event.target)) {
                searchSuggestions.innerHTML = '';
            }
        }

        // Handle family card search fields
        familySearchFields.forEach(({ inputSelector, suggestionsContainerSelector }) => {
            const inputElement = document.querySelector(inputSelector);
            const suggestionsElement = document.querySelector(suggestionsContainerSelector);

            if (inputElement && suggestionsElement) {
                if (!inputElement.contains(event.target) && !suggestionsElement.contains(event.target)) {
                    suggestionsElement.innerHTML = '';
                }
            }
        });
    });
});
