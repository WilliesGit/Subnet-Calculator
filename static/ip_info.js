

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

        const errorSeg = document.querySelector('.error-message.error-seg');
        const errorCidrSeg = document.querySelector('.error-message.error-cidr');


        
        // Basic validation: ensure fields aren't empty
        

        if (!ipAddress) {
            ipInput.classList.add('input-error');
            document.querySelector('.error-seg').textContent = 'Please enter an IP address';
            document.querySelector('.error-seg').style.display = 'block';
            return;
        } 
        else {
            ipInput.classList.remove('input-error');
            document.querySelector('.error-seg').style.display = 'none';
        }
        

        if (!subnetMaskValue) {
            subnetMask.classList.add('input-error');
            document.querySelector('.error-cidr').textContent = 'Please enter a subnet mask';
            document.querySelector('.error-cidr').style.display = 'block';
            return;
        } 
        else {
            subnetMask.classList.remove('input-error');
            document.querySelector('.error-cidr').style.display = 'none';

        }


        // Send data to Flask API
        try {
            const response = await fetch('/api/ip_info', {
                method: 'POST',
                headers: {'Content-Type': 'application/json',},  // Tell backend our body is JSON
                body: JSON.stringify({ // Convert subnets JS object into JSON string
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



