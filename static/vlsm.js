
/*** ===== SUBNET CALCULATOR INTERACTION ===== ***/
const form = document.querySelector('.panel');
const tableBody = document.querySelector('.table tbody'); // target your table body



if (form && tableBody) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault(); // prevent normal page reload
       // console.log("✅ Form submit handler triggered");

        // Get IP address and subnet mask from inputs
        // Get inputs
        const ipInput = document.querySelector('.seg');
        const subnetMask = document.querySelector('.cidr-seg');
        const hostsInput = document.querySelector('.hosts-seg');

        const ipAddress = ipInput.value.trim();
        const subnetMaskValue = subnetMask.value.trim();
        const hostsValue = hostsInput.value.trim();


        // Basic validation: ensure fields aren't empty
        if(!ipAddress && !subnetMaskValue && !hostsValue){
           const hint_text =  document.querySelector('.hint')
           hint_text.style.color = 'red';
           hint_text.style.border = '1px solid #f5a5a5';
           hint_text.style.borderRadius = '3px';
           hint_text.style.backgroundColor = '#ebc8d0ff';
           hint_text.style.padding = '8px 10px';
           return;
        }
        else{
            const hint_text =  document.querySelector('.hint')
            hint_text.style.color = '#475569';
            hint_text.style.border = 'none';
            hint_text.style.backgroundColor = 'transparent';
            hint_text.classList.remove('red')
        }

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
            document.querySelector('.error-cidr').textContent = 'Please enter CIDR notation or a subnet mask';
            document.querySelector('.error-cidr').style.display = 'block';
            return;
        } 
        else {
            subnetMask.classList.remove('input-error');
            document.querySelector('.error-cidr').style.display = 'none';

        }

        if(!hostsValue) {
            hostsInput.classList.add('input-error');
            document.querySelector('.error-hosts').textContent = 'Please enter no. of hosts';
            document.querySelector('.error-hosts').style.display = 'block';
            return;
        } 
        else {
            hostsInput.classList.remove('input-error');
            document.querySelector('.error-hosts').style.display = 'none';

        }

        //Table update notification
        const form_btn = document.querySelector('.btn')
        const notification =  document.querySelector('.notification')
        const notify_message =  document.querySelector('.notify_message')
        const loader_container = document.querySelector('.loader-container');
    

        if(ipAddress && subnetMaskValue && form_btn){
            loader_container.classList.add('loader-show');
        }



        // Send data to Flask API
        try {
            const response = await fetch('/api/vlsm', {
                method: 'POST',
                headers: {'Content-Type': 'application/json',},
                body: JSON.stringify({
                    ip_address: ipAddress,
                    subnet_mask: subnetMaskValue,
                    no_of_hosts: hostsValue,
                    ip_version: 4 // Hardcoded for IPv4 form
                })
            });

            const result = await response.json();

            if (!response.ok) {
                alert(result.error || 'Error processing request');
                return;
            }

           

            // Show loader for minimum 1.5 seconds to feel responsive
            setTimeout(() => {
                // Start fade out animation
                loader_container.classList.add('loader-hide');
                loader_container.classList.remove('loader-show');
                
                // Wait for fade-out animation to complete (750ms)
                setTimeout(() => {
                    // Hide loader completely after fade-out
                    loader_container.classList.remove('loader-hide');
                    
                   
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
                            <td>${subnet.broadcast}</td>
                            <td>${subnet.first}</td>
                            <td>${subnet.last}</td>
                            <td>${subnet.hosts}</td>
                        `;
                        tableBody.appendChild(row);
                    });

                    // Show notification immediately after table update
                    notify_message.textContent = 'Table updated successfully';
                    notification.style.display = 'flex';
                    
                    // Hide notification after 2.5 seconds (shorter for better UX)
                    setTimeout(() => {
                        notification.classList.add('hide');
                        setTimeout(() => {
                            notification.style.display = 'none';
                            notification.classList.remove('hide');
                        }, 300); // Match CSS animation duration
                    }, 2500);
                    
                }, 750); // Wait 750ms for loader fade-out animation to complete
                
            }, 2000); // Show loader for 1.5 seconds



            // Optional: Scroll table into view after update
            document.querySelector('.table-wrapper').scrollIntoView({ behavior: 'smooth' });

        } catch (err) {
            console.error('Error fetching IP info:', err);
            alert('Failed to connect to server');
        }
    });
}


