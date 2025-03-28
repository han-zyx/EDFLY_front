

document.getElementById("showMoreBtn").addEventListener("click", function() {
    document.getElementById("moreDiagrams").style.display = "block";
    this.style.display = "none";
});



document.getElementById("showMoreBtn").addEventListener("click", function() {
    document.getElementById("moreDiagrams").style.display = "block";
    this.style.display = "none";
});


document.addEventListener('DOMContentLoaded', function() {
    // Add active class to current page link
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPage) {
            link.classList.add('active');
        }
    });

    // Add table row click handler (optional)
    const tableRows = document.querySelectorAll('.table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('click', function() {
            console.log('Row clicked:', this.cells[3].textContent);
            // Add your row click functionality here
        });
    });
});