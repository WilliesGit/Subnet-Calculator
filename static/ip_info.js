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

    console.log('script.js fully loaded');
});
