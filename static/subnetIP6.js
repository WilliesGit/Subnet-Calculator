


  


/*** ===== SUBNET CALCULATOR INTERACTION ===== ***/
const form = document.querySelector('.panel');
const tableBody = document.querySelector('.table tbody'); // target your table body



if (form && tableBody) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault(); // prevent normal page reload
        console.log("✅ Form submit handler triggered");

        // Get IP address and subnet mask from inputs
        // Get inputs
        const ipInput = document.querySelector('.seg');
        const subnetMask = document.querySelector('.cidr-seg');
        const hostsInput = document.querySelector('.hosts-seg');

        const ipAddress = ipInput.value.trim();
        const subnetMaskValue = subnetMask.value.trim();
        const hostsValue = hostsInput.value.trim();

        // Basic validation: ensure fields aren't empty
        if (!ipAddress || !subnetMaskValue || !hostsValue) {
            alert('Please enter an IP address, subnet mask and required host.');
            return;
        }

        if (isNaN(hostsValue) || parseInt(hostsValue) <= 0) {
            alert('Please enter a valid positive integer for required hosts.(fixed-length)');
            return;
        }



        // Send data to Flask API
        try {
            const response = await fetch('/api/IPv6subnet', {
                method: 'POST',
                headers: {'Content-Type': 'application/json',},
                body: JSON.stringify({
                    ip_address: ipAddress,
                    subnet_mask: subnetMaskValue,
                    no_of_hosts: hostsValue,
                    ip_version: 6 // Hardcoded for IPv6 form
                })
            });

            const result = await response.json();

            if (!response.ok) {
                alert(result.error || 'Error processing request');
                return;
            }

            // Clear existing rows
            tableBody.innerHTML = '';

            if (result.subnets && result.subnets.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="5" class="p-2 border text-red-600">No subnets generated.</td></tr>`;
                return;
            }

            // Update table with new subnet data
            result.subnets.forEach(subnet => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${subnet.subnet}</td>
                    <td>${subnet.network}</td>
                    <td>${subnet.first}</td>
                    <td>${subnet.last}</td>
                `;
                tableBody.appendChild(row);
            });

            // Optional: Scroll table into view after update
            document.querySelector('.table-wrapper').scrollIntoView({ behavior: 'smooth' });

        } catch (err) {
            console.error('Error fetching IP info:', err);
            alert('Failed to connect to server');
        }
    });
}

