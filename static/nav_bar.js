const links = document.querySelectorAll('.desktop-nav a, .mobile-nav a');
const sections = document.querySelectorAll('.placeholder-content-other');

// Mobile menu toggle functionality
const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
const mobileNav = document.querySelector('.mobile-nav');

if (mobileMenuToggle && mobileNav) {
    mobileMenuToggle.addEventListener('click', () => {
        mobileMenuToggle.classList.toggle('active');
        mobileNav.classList.toggle('active');
    });

    // Close mobile menu when clicking on a link
    document.querySelectorAll('.mobile-nav a').forEach(link => {
        link.addEventListener('click', () => {
            mobileMenuToggle.classList.remove('active');
            mobileNav.classList.remove('active');
        });
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!mobileMenuToggle.contains(e.target) && !mobileNav.contains(e.target)) {
            mobileMenuToggle.classList.remove('active');
            mobileNav.classList.remove('active');
        }
    });
}

// Hide all sections and remove active class from links
function showSection(targetId){
    sections.forEach(section => section.classList.remove('active'));
    links.forEach(link => link.classList.remove('active'));

// Show the target section and highlight its link
    const target = document.getElementById(targetId);
    if (target) {
        target.classList.add('active');
        const targetLink = document.querySelector(`.desktop-nav a[href="#${targetId}"], .mobile-nav a[href="#${targetId}"]`);
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
    // Update both desktop and mobile nav links
    document.querySelectorAll('.desktop-nav a, .mobile-nav a').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === '#' + current) {
            link.classList.add('active');
        }
    });
}



window.addEventListener('scroll', highlightNav);
highlightNav(); // Initial call