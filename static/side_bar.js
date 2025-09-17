// Wait for the page to fully load
document.addEventListener('DOMContentLoaded', () => {

      /*** ===== SIDEBAR ACTIVE ITEM HANDLER ===== ***/
    const menuItems = document.querySelectorAll('#sidebar-menu .sidebar-item');
    menuItems.forEach(item => {
        item.addEventListener('click', (e) => {
            const link = item.querySelector('a');
            const href = link.getAttribute('href');
            
            // Only toggle active class and prevent default for placeholder links (#)
            if (href === '#') {
                e.preventDefault();
                menuItems.forEach(i => i.classList.remove('active'));
                item.classList.add('active');
            } else {
                // For valid links (e.g., /ipv4_calculator), update active class and allow navigation
                menuItems.forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                // Navigation happens automatically via the <a> tag
            }
        });
    }); 



    console.log('script.js fully loaded');
});