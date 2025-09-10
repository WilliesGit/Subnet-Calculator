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


    /*** ===== SUBNET CALCULATOR INTERACTION ===== ***/
    const form = document.querySelector('.panel');
    const tableBody = document.querySelector('.table tbody'); // target your table body

    if (form && tableBody) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault(); // prevent normal page reload
            console.log("✅ Form submit handler triggered");

           // Get IP address and subnet mask from inputs
            const ipInput = document.querySelector('.seg');
            const subnetMask = document.querySelector('.cidr-seg');
            const ipAddress = ipInput.value.trim();
            const subnetMaskValue = subnetMask.value.trim();

            // Basic validation: ensure fields aren't empty
            if (!ipAddress || !subnetMaskValue) {
                alert('Please enter an IP address and subnet mask.');
                return;
            }

            // Send data to Flask API
            try {
                const response = await fetch('/api/ip_info', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json',},
                    body: JSON.stringify({
                        ip_address: ipAddress,
                        subnet_mask: subnetMaskValue
                    })
                });

                const result = await response.json();

                if (!response.ok) {
                    alert(result.error || 'Error processing request');
                    return;
                }

                // Clear existing rows
                tableBody.innerHTML = '';

                // Insert new row with returned values
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${result.network_address}</td>
                    <td>${result.broadcast_address}</td>
                    <td>${result.first_address}</td>
                    <td>${result.last_address}</td>
                `;
                tableBody.appendChild(row);

                // Optional: Scroll table into view after update
                document.querySelector('.table-wrapper').scrollIntoView({ behavior: 'smooth' });

            } catch (err) {
                console.error('Error fetching IP info:', err);
                alert('Failed to connect to server');
            }
        });
    }

    const table_actions = document.querySelector('.table-actions');

    if(table_actions){
        const btn_export = document.querySelector('.btn-export');
        btn_export.onclick = function(){
            window.alert('Export button clicked')
    } 
    }
    //

    //const export_btn = document.getElementById('btn-export');
    //export_btn.onclick = function(){
        //export_btn.textContent = alert('Export button clicked')
    //}
    

    console.log('script.js fully loaded');
});
