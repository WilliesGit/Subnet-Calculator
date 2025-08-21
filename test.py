import random
import ipaddress

def RandomIP(ip_address, subnet_mask, ip_version=4):
    try:
        # Validate and parse IP (returns IP object and version number)
        ip, ip_version = ValidateIP(ip_address)
        
        # Parse subnet (CIDR prefix as int, from mask or /notation)
        prefix = ParseSubnet(subnet_mask, ip_version)
        
        # Calculate network object (IPv4 or IPv6)
        network = ipaddress.ip_network(f"{ip}/{prefix}", strict=False)
        
        # Error if actual version doesn't match requested version
        if network.version != ip_version:
            return {'error': f"IP version mismatch: {network.version} vs {ip_version}"}
        
        # ==== For IPv4 ====
        if ip_version == 4:
            # 'network.network_address': first address in subnet (e.g., 192.168.1.0)
            # 'network.broadcast_address': last ("broadcast") address (e.g., 192.168.1.255)
            
            # These are integers! We add 1 to skip the network address, and subtract 1 for broadcast
            low = int(network.network_address) + 1
            high = int(network.broadcast_address) - 1
            
            # Total number of usable hosts (all values between low and high, inclusive)
            count = high - low + 1
            
            if count <= 0:
                return {'error': "No usable hosts available in this subnet."}
            
            # Randomly pick an integer in usable host range
            rand_ip_int = random.randint(low, high)
            
            # Convert that integer back to a dotted IPv4 address
            random_ip = ipaddress.IPv4Address(rand_ip_int)
            broadcast = str(network.broadcast_address)
        
        # ==== For IPv6 ====
        else:
            # No broadcast address for IPv6 (so we set broadcast = 'N/A')
            broadcast = 'N/A'
            
            # Here, we avoid network address, and pick a random address within the subnet
            # Lowest is network.network_address + 1
            low = int(network.network_address) + 1
            # Highest is last address in the subnet: network_address + num_addresses - 1
            high = int(network.network_address) + network.num_addresses - 1
            
            count = high - low + 1
            
            if count <= 0:
                return {'error': "No usable hosts available in this subnet."}
            
            # Pick random integer between low and high
            rand_ip_int = random.randint(low, high)
            
            # Convert integer to IPv6 (colon format)
            random_ip = ipaddress.IPv6Address(rand_ip_int)

        # Return dictionary with network, broadcast, and random_ip as plain strings
        return {
            'network': str(network.network_address),
            'broadcast': broadcast,
            'random_ip': str(random_ip)
        }
    except ValueError as e:
        return {'error': str(e)}
