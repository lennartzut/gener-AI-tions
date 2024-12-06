import { setupIndividualSearch } from './common.js';

document.addEventListener('DOMContentLoaded', function () {
    setupIndividualSearch({
        inputSelector: '#parentName',  // For adding parents
        suggestionsContainerSelector: '#parentSuggestions',
        excludeId: null,
        minQueryLength: 2,
        onSelect: function (individual) {
            // Set the hidden input field value to selected individual's ID
            document.getElementById('parentId').value = individual.id;
        }
    });

    setupIndividualSearch({
        inputSelector: '#partnerName',  // For adding partners
        suggestionsContainerSelector: '#partnerSuggestions',
        excludeId: null,
        minQueryLength: 2,
        onSelect: function (individual) {
            // Set the hidden input field value to selected individual's ID
            document.getElementById('partnerId').value = individual.id;
        }
    });

    setupIndividualSearch({
        inputSelector: '#childName',  // For adding children
        suggestionsContainerSelector: '#childSuggestions',
        excludeId: null,
        minQueryLength: 2,
        onSelect: function (individual) {
            // Set the hidden input field value to selected individual's ID
            document.getElementById('childId').value = individual.id;
        }
    });

    // Hide suggestions when clicking outside of search input or suggestions list
    document.addEventListener('click', function (event) {
        const inputsAndSuggestions = [
            {input: document.getElementById('parentName'), suggestions: document.getElementById('parentSuggestions')},
            {input: document.getElementById('partnerName'), suggestions: document.getElementById('partnerSuggestions')},
            {input: document.getElementById('childName'), suggestions: document.getElementById('childSuggestions')}
        ];

        inputsAndSuggestions.forEach(({ input, suggestions }) => {
            if (input && suggestions && !input.contains(event.target) && !suggestions.contains(event.target)) {
                suggestions.innerHTML = '';
            }
        });
    });
});
