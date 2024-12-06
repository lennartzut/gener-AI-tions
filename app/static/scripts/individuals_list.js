document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const individualsList = document.getElementById('individualsList');
    const listItems = Array.from(individualsList.getElementsByClassName('list-group-item'));

    if (searchInput) {
        searchInput.addEventListener('input', function () {
            const query = searchInput.value.trim().toLowerCase();

            // Filter individuals based on search query
            listItems.forEach((item) => {
                const itemText = item.textContent.toLowerCase();
                if (itemText.includes(query)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
});
