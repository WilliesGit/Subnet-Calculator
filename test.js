// Wait for the page to fully load
document.addEventListener('DOMContentLoaded', () => {
    /*** ===== SIDEBAR ACTIVE ITEM HANDLER ===== ***/
    const menuItems = document.querySelectorAll('#sidebar-menu .sidebar-item');
    menuItems.forEach(item => {
        item.addEventListener('click', (e) => {
            const link = item.querySelector('a');
            const href = link.getAttribute('href');
            if (href === '#') {
                e.preventDefault();
                menuItems.forEach(i => i.classList.remove('active'));
                item.classList.add('active');
            } else {
                menuItems.forEach(i => i.classList.remove('active'));
                item.classList.add('active');
            }
        });
    });



/*** ===== RANDOM IP GENERATOR INTERACTION ===== ***/
    const form = document.querySelector('.random-ip-form');
    const tableBody = document.querySelector('#random-ip-table');

    // Function to validate inputs
    function validateInputs(ipInput, subnetMask, versionInput) {
        const ipAddress = ipInput.value.trim();
        const subnetMaskValue = subnetMask.value.trim();
        const ipVersion = versionInput.value;
        if (!ipAddress || !subnetMaskValue) {
            return { valid: false, error: 'Please enter IP address and subnet mask.' };
        }
        if (!['4', '6'].includes(ipVersion)) {
            return { valid: false, error: 'Please select a valid IP version (IPv4 or IPv6).' };
        }
        return { valid: true, data: { ipAddress, subnetMaskValue, ipVersion } };
    }

    // Function to fetch random IP
    async function fetchRandomIp(ipAddress, subnetMaskValue, ipVersion) {
        try {
            const response = await fetch('/api/random_ip', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ip_address: ipAddress,
                    subnet_mask: subnetMaskValue,
                    ip_version: ipVersion
                })
            });
            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.error || 'Unknown error from server');
            }
            return result;
        } catch (err) {
            throw new Error(`Failed to fetch random IP: ${err.message}`);
        }
    }

    // Function to update table
    function updateTable(tableBody, data) {
        tableBody.innerHTML = '';
        if (data.error) {
            tableBody.innerHTML = `<tr><td colspan="3" class="p-2 border text-red-600">${data.error}</td></tr>`;
            return;
        }
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="p-2 border">${data.network}</td>
            <td class="p-2 border">${data.broadcast}</td>
            <td class="p-2 border">${data.random_ip}</td>
        `;
        tableBody.appendChild(row);
    }

    // Form submission handler
    if (form && tableBody) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log("✅ Random IP form submitted");

            const ipInput = form.querySelector('.seg');
            const subnetMask = form.querySelector('.cidr-seg');
            const versionInput = form.querySelector('.ip-version');

            const validation = validateInputs(ipInput, subnetMask, versionInput);
            if (!validation.valid) {
                tableBody.innerHTML = `<tr><td colspan="3" class="p-2 border text-red-600">${validation.error}</td></tr>`;
                return;
            }

            try {
                const result = await fetchRandomIp(
                    validation.data.ipAddress,
                    validation.data.subnetMaskValue,
                    validation.data.ipVersion
                );
                updateTable(tableBody, result);
                document.querySelector('.table-wrapper').scrollIntoView({ behavior: 'smooth' });
            } catch (err) {
                console.error('Error:', err.message);
                tableBody.innerHTML = `<tr><td colspan="3" class="p-2 border text-red-600">${err.message}</td></tr>`;
            }
        });
    }

    console.log('random_ip.js fully loaded');
});