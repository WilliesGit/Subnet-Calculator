
/*** ===== RANDOM CALCULATOR INTERACTION ===== ***/
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
            const response = await fetch('/api/random_ip', {
                method: 'POST',
                headers: {'Content-Type': 'application/json',},
                body: JSON.stringify({
                    ip_address: ipAddress,
                    subnet_mask: subnetMaskValue,
                    ip_version: 4
                    
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
                <td>${result.network}</td>
                <td>${result.broadcast}</td>
                <td>${result.random_ip}</td>
                
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


