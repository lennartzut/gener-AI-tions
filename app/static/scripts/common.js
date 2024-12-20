// common.js
// Generic utility functions that can be used by multiple modules

export function toggleDeathFields() {
    const isDeceased = document.getElementById('isDeceased')?.checked;
    const isDeceasedUnknown = document.getElementById('isDeceasedUnknown')?.checked;
    const deathFields = document.getElementById('deathFields');

    if (deathFields) {
        deathFields.style.display = (isDeceased && !isDeceasedUnknown) ? 'block' : 'none';
    }
}
