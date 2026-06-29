const navButtons = document.querySelectorAll('.top-buttons a');
const panels = document.querySelectorAll('.content-panel');

navButtons.forEach((button) => {
    button.addEventListener('click', (event) => {
        event.preventDefault();

        navButtons.forEach((btn) => btn.classList.remove('active'));
        button.classList.add('active');

        const targetId = button.getAttribute('data-target');
        panels.forEach((panel) => {
            panel.classList.toggle('active', panel.id === targetId);
        });
    });
});

window.addEventListener('load', () => {
    document.body.classList.add('loaded');
});
