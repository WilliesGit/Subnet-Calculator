

/*** ===== SUBNET CALCULATOR INTERACTION ===== ***/
const form = document.querySelector('.panel');
const tableBody = document.querySelector('.table tbody'); // target your table body

if (form && tableBody) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault(); // prevent normal page reload
        //console.log("✅ Form submit handler triggered");

        // Get IP address and subnet mask from inputs
        const ipInput = document.querySelector('.seg');
        const subnetMask = document.querySelector('.cidr-seg');
        const ipAddress = ipInput.value.trim();
        const subnetMaskValue = subnetMask.value.trim();

     

        
        // Basic validation: ensure fields aren't empty
        if(!ipAddress && !subnetMaskValue){
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
        
        //Table update notification
        const form_btn = document.querySelector('.btn')
        const notification =  document.querySelector('.notification')
        const notify_message =  document.querySelector('.notify_message')
    

        if(ipAddress && subnetMaskValue && form_btn){
            notify_message.textContent = 'Table updated successfully';
            notification.style.display = 'flex';
        }

    
        //Hide notification after 3 seconds
        setTimeout(() => {
            notification.classList.add('hide');
            setTimeout(() => {
                notification.style.display = 'none';
                //notify_icon.style.display = 'none';
                notification.classList.remove('hide');
            }, 300); // Match this duration with the CSS animation duration
        }, 3000)
        
        

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
            //console.error('Error fetching IP info:', err);
            alert('Failed to connect to server');
        }
    });
}



