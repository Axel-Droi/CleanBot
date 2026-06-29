document.querySelectorAll('.top-buttons a').forEach((button) => {
    button.addEventListener('click', (event) => {
        event.preventDefault();
        document.querySelectorAll('.top-buttons a').forEach((btn) => btn.classList.remove('active'));
        button.classList.add('active');
    });
});

window.addEventListener('load', () => {
    document.body.classList.add('loaded');
});
