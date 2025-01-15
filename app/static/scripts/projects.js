// File: static/scripts/projects.js
document.addEventListener('DOMContentLoaded', () => {
    const updateProjectModal = document.getElementById('updateProjectModal');
    const deleteProjectModal = document.getElementById('deleteProjectModal');

    if (updateProjectModal) {
        updateProjectModal.addEventListener('show.bs.modal', (event) => {
            const button = event.relatedTarget;
            const projectId = button.getAttribute('data-project-id');
            const projectName = button.getAttribute('data-project-name');

            // Grab the form in the modal
            const form = updateProjectModal.querySelector('#updateProjectForm');
            // Set the action to match /projects/<int:project_id>/update
            form.action = `/projects/${projectId}/update`;

            // Fill in the name field
            const projectNameInput = updateProjectModal.querySelector('#updateProjectName');
            projectNameInput.value = projectName;
        });
    }

    if (deleteProjectModal) {
        deleteProjectModal.addEventListener('show.bs.modal', (event) => {
            const button = event.relatedTarget;
            const projectId = button.getAttribute('data-project-id');
            const projectName = button.getAttribute('data-project-name');

            // Grab the form in the modal
            const form = deleteProjectModal.querySelector('#deleteProjectForm');
            // Set the action to match /projects/<int:project_id>/delete
            form.action = `/projects/${projectId}/delete`;

            // Show project name in the modal text
            const projectNameSpan = deleteProjectModal.querySelector('#deleteProjectName');
            projectNameSpan.textContent = projectName;
        });
    }
});
