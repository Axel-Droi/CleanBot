document.querySelectorAll('.top-buttons a').forEach((button) => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.top-buttons a').forEach((btn) => btn.classList.remove('active'));
        button.classList.add('active');
    });
});
