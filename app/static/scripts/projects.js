document.addEventListener('DOMContentLoaded', () => {
    const updateProjectModal = document.getElementById('updateProjectModal');
    const deleteProjectModal = document.getElementById('deleteProjectModal');

    if (updateProjectModal) {
        updateProjectModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const projectId = button.getAttribute('data-project-id');
            const projectName = button.getAttribute('data-project-name');
            const form = updateProjectModal.querySelector('#updateProjectForm');
            form.action = `update_project/${projectId}`;
            const projectNameInput = updateProjectModal.querySelector('#updateProjectName');
            projectNameInput.value = projectName;
        });
    }

    if (deleteProjectModal) {
        deleteProjectModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const projectId = button.getAttribute('data-project-id');
            const projectName = button.getAttribute('data-project-name');

            const form = deleteProjectModal.querySelector('#deleteProjectForm');
            form.action = `delete_project/${projectId}`;

            const projectNameSpan = deleteProjectModal.querySelector('#deleteProjectName');
            projectNameSpan.textContent = projectName;
        });
    }
});
