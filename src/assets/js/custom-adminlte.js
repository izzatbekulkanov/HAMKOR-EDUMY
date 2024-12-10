document.addEventListener("DOMContentLoaded", function () {
    console.log("Custom AdminLTE JS loaded!");
    const themeToggleButton = document.querySelector('#theme-toggle');
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', function () {
            document.body.classList.toggle('dark-mode');
        });
    }
});
