const links = document.querySelectorAll('nav a');
const sections = document.querySelectorAll('.placeholder-content-other');

// Hide all sections and remove active class from links
function showSection(targetId){
    sections.forEach(section => section.classList.remove('active'));
    links.forEach(link => link.classList.remove('active'));

// Show the target section and highlight its link
    const target = document.getElementById(targetId);
    if (target) {
        target.classList.add('active');
        const targetLink = document.querySelector(`nav a[href="#${targetId}"]`);
        if (targetLink) targetLink.classList.add('active');
        target.scrollIntoView({ behavior: 'smooth' });
    }
}

// Smooth scrolling on click
links.forEach(link => {
    link.addEventListener('click', e => {
        e.preventDefault();
        const targetId = link.getAttribute('href').substring(1);
        showSection(targetId);
    });
});

// Scroll spy
function highlightNav() {
    let current = '';
    sections.forEach(section => {
        const rect = section.getBoundingClientRect();
        if (rect.top <= window.innerHeight / 2 && rect.bottom >= window.innerHeight / 2) {
            current = section.id;
        }
    });
    links.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === '#' + current) {
            link.classList.add('active');
        }
    });
}



window.addEventListener('scroll', highlightNav);
highlightNav(); // Initial call