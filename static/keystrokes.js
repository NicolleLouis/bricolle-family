// Global keyboard shortcuts for Bricolle Family
// Navigates to the documents list when Ctrl+Alt+D is pressed

document.addEventListener('keydown', function (event) {
    if (event.ctrlKey && event.altKey && event.key.toLowerCase() === 'p') {
        window.location.href = '/documents/';
    }
});
