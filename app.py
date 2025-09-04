from flask import Flask, request, jsonify, Response, render_template, url_for, send_from_directory
import io
import ipaddress
import random
import re
import math
import csv

app = Flask(__name__)

# -------------------------------
# HTML Route
# -------------------------------
@app.route("/")
def home():
    # Renders templates/index.html
    return render_template("index.html")

# -------------------------------
# Utility Functions (unchanged)
# -------------------------------
def ValidateIP(ip_address):
    try:
        ip = ipaddress.ip_address(ip_address)
        return ip, ip.version
    except ValueError:
        raise ValueError(f"Invalid IP address: {ip_address}")

def IPv4ParseSubnet(subnet_mask, ip_version=4):
    if isinstance(subnet_mask, str) and subnet_mask.startswith('/'):
        subnet_mask = subnet_mask[1:] 

    if ip_version == 4:
        #Checks if subnet_mask is in CIDR notation (a number like 24) for IPv4
        if re.match(r'^\d{1,2}$', subnet_mask):
            prefix = int(subnet_mask)
            if 0 <= prefix <= 32:
                return prefix
            raise ValueError(f"IPv4 CIDR prefix must be between 0 and 32: {subnet_mask}")
        try:
            mask = ipaddress.IPv4Address(subnet_mask)
            return bin(int(mask)).count('1') #Converts subnet mask into into subnet prefix 
        except ValueError:
            raise ValueError(f"Invalid IPv4 subnet mask: {subnet_mask}")
    else:
        raise ValueError(f'Invalid IPv4 version. Must be an IPv4 Address')

def ParseSubnet(subnet_mask, ip_version=4):
    """ Convert a subnet mask to CIDR prefix length for IPv4 or IPv6."""
  # Handle CIDR with or without leading '/'
    if isinstance(subnet_mask, str) and subnet_mask.startswith('/'):
        subnet_mask = subnet_mask[1:] 

    if ip_version == 4:
        #Checks if subnet_mask is in CIDR notation (a number like 24) for IPv4
        if re.match(r'^\d{1,2}$', subnet_mask):
            prefix = int(subnet_mask)
            if 0 <= prefix <= 32:
                return prefix
            raise ValueError(f"IPv4 CIDR prefix must be between 0 and 32: {subnet_mask}")
        try:
            mask = ipaddress.IPv4Address(subnet_mask)
            return bin(int(mask)).count('1') #Converts subnet mask into into subnet prefix 
        except ValueError:
            raise ValueError(f"Invalid IPv4 subnet mask: {subnet_mask}")
        
    elif ip_version == 6:
        if re.match(r'^\d{1,3}$', subnet_mask):
            prefix = int(subnet_mask)
            if 0 <= prefix <= 128:
                return prefix
            raise ValueError(f"IPv6 CIDR prefix must be between 0 and 128: {subnet_mask}")
        raise ValueError(f"IPv6 subnet mask must be in CIDR notation (0-128)): {subnet_mask}")
    raise ValueError(f"Unsupported IP version: {ip_version}")


def NetAddr(ip_address, subnet_mask):
    interface = ipaddress.ip_interface(f"{ip_address}/{subnet_mask}") 
    return str(interface.network.network_address)


def BroadAddr(ip_address, subnet_mask):
    interface = ipaddress.ip_interface(f"{ip_address}/{subnet_mask}")
    return str(interface.network.broadcast_address)


def FirstAddr(ip_address, subnet_mask):
    interface = ipaddress.ip_interface(f"{ip_address}/{subnet_mask}")
    first_add = next(interface.network.hosts(), None)
    return str(first_add) if first_add else None


def LastAddr(ip_address, subnet_mask):
    interface = ipaddress.ip_interface(f"{ip_address}/{subnet_mask}")
    network = interface.network
    num_hosts = network.num_addresses - 2
    if num_hosts <= 0:
        return None
    last_host = ipaddress.ip_address(int(network.network_address) + num_hosts)
    return str(last_host)


def No_Of_Hosts(ip_address, subnet_mask):
    interface = ipaddress.ip_interface(f"{ip_address}/{subnet_mask}")
    return interface.network.num_addresses - 2


def Find_Prefix(hosts, ip_version=4):
    if hosts < 0:
        raise ValueError("Number of hosts must be non-negative")
    total_bits = 32 if ip_version == 4 else 128
    needed_addresses = hosts + 2
    bits_for_addresses = math.ceil(math.log2(needed_addresses)) if needed_addresses > 0 else 0
    prefix = total_bits - bits_for_addresses
    if prefix < 0:
        raise ValueError(f"Too many hosts ({hosts}) for IPv{ip_version}")
    return prefix



def IPv4Subnet_Split(ip_address, subnet_mask, no_of_hosts, ip_version=4):
    #Validate input for IPv4 Address
    try:
        ip_address = ipaddress.ip_address(ip_address)
        if ip_address.version != 4:
            raise ValueError("Only IPv4 addresses are supported, not IPv6")
    except ValueError as e:
        raise ValueError(f"Invalid IPv4 address: {ip_address} ")
    
    network = ipaddress.ip_network(f"{ip_address}/{subnet_mask}", strict=False)
    ip_version = network.version
    subnets = []

    try:
        if not isinstance(no_of_hosts, int) or no_of_hosts <=0:
            raise ValueError("Host input must be an integer (fixed-length)")
        
      
        new_prefix = Find_Prefix(no_of_hosts, ip_version)
        if new_prefix < network.prefixlen:
            raise ValueError(f"New prefix {new_prefix} must be greater than or equal to the original prefix {network.prefixlen}")
        subnets_prefix = network.subnets(new_prefix=new_prefix)

        for index, subnet in enumerate(subnets_prefix, start=1):
            subnet_addr = str(subnet.network_address)

            subnets.append({
                'subnet': f"Subnet {index}",  # For table
                'network': f"{str(NetAddr(subnet_addr, new_prefix))}/{new_prefix}",
                'broadcast': str(BroadAddr(subnet_addr, new_prefix)),
                'first': str(FirstAddr(subnet_addr, new_prefix)),
                'last': str(LastAddr(subnet_addr, new_prefix))
            })
               
    except ValueError as e:
        return {'error': str(e)}
    
    return {'subnets': subnets, 'total': len(subnets)}


def Subnet_Split(ip_address, subnet_mask, no_of_hosts, ip_version=4):
    network = ipaddress.ip_network(f"{ip_address}/{subnet_mask}", strict=False)
    ip_version = network.version
    subnets = []
    max_subnets = 1000 if ip_version == 6 else float('inf')
    try:
        if isinstance(no_of_hosts, int):
            new_prefix = Find_Prefix(no_of_hosts, ip_version)
            if new_prefix < network.prefixlen:
                raise ValueError(f"New prefix {new_prefix} must be greater than or equal to the original prefix {network.prefixlen}")
            subnets_prefix = network.subnets(new_prefix=new_prefix)

            for index, subnet in enumerate(subnets_prefix, start=1):
                subnet_addr = str(subnet.network_address)

                if ip_version == 4:
                    ip_last = str(LastAddr(subnet_addr, new_prefix))
                else:
                    # For IPv6, calculate last address as network address + total addresses - 1
                    network = ipaddress.ip_network(f"{subnet_addr}/{new_prefix}", strict=False)
                    last_ipv6_int = int(network.network_address) + network.num_addresses - 1
                    ip_last = str(ipaddress.IPv6Address(last_ipv6_int))

                subnets.append({
                    'subnet': f"Subnet {index}",  # For table
                    'network': f"{str(NetAddr(subnet_addr, new_prefix))}/{new_prefix}",
                    'broadcast': str(BroadAddr(subnet_addr, new_prefix)) if ip_version == 4 else 'N/A',
                    'first': str(FirstAddr(subnet_addr, new_prefix)),
                    'last': ip_last
                })
                if index >= max_subnets:
                    break
        elif isinstance(no_of_hosts, list):
            host_counts = sorted(no_of_hosts, reverse=True)
            current_network = int(network.network_address)

            for index, hosts in enumerate(host_counts, start=1):
                new_prefix = Find_Prefix(hosts, ip_version)
                subnet_network = ipaddress.ip_network(f"{ipaddress.ip_address(current_network)}/{new_prefix}", strict=False)

                if not network.supernet_of(subnet_network):
                    raise ValueError(f"Subnet {index} ({subnet_network}) does not fit in {network}")

                subnet_addr = str(subnet_network.network_address)

                if ip_version == 4:
                    ip_last = str(LastAddr(subnet_addr, new_prefix))
                else:
                    last_ipv6_int = int(subnet_network.network_address) + subnet_network.num_addresses - 1
                    ip_last = str(ipaddress.IPv6Address(last_ipv6_int))

                subnets.append({
                    'subnet': f"Subnet {index}",
                    'network': f"{str(NetAddr(subnet_addr, new_prefix))}/{new_prefix}",
                    'broadcast': str(BroadAddr(subnet_addr, new_prefix)) if ip_version == 4 else 'N/A',
                    'first': str(FirstAddr(subnet_addr, new_prefix)),
                    'last': ip_last
                })

                current_network += subnet_network.num_addresses

                if current_network > int(network.broadcast_address):
                    raise ValueError(f"Cannot fit all subnets in {network}")

                if index >= max_subnets:
                    break

        else:
            raise ValueError("Host input must be an integer (fixed-length) or a list (VLSM)")
        return {'subnets': subnets, 'total': len(subnets)}
    except ValueError as e:
        return {'error': str(e)}


def RandomIP(ip_address, subnet_mask, ip_version=4):
    try:
        ip, ip_version = ValidateIP(ip_address)

        prefix = ParseSubnet(subnet_mask, ip_version)

        network = ipaddress.ip_network(f"{ip}/{prefix}", strict=False)

        if network.version != ip_version:
            return {'error': f"IP version mismatch: {network.version} vs {ip_version}"}

        # ==== For IPv4 ====
        if ip_version == 4:
           # These are integers! We add 1 to skip the network address, and subtract 1 for broadcast
           first_addr_int = int(network.network_address) + 1
           last_addr_int = int(network.broadcast_address) - 1


            # Calculate the number of usable host addresses in the subnet.
            # The usable range is inclusive, so we add 1.
           count = last_addr_int - first_addr_int + 1

           if count <= 0:
                return {'error': "No usable hosts available in this subnet."}
           
            # Randomly pick an integer in usable host range
           rand_ip_int = random.randint(first_addr_int, last_addr_int) 

           # Convert that integer back to a dotted IPv4 address
           random_ip = ipaddress.IPv4Address(rand_ip_int)
           broadcast = str(network.broadcast_address)

        # ==== For IPv6 ====
        else:
            broadcast = 'N/A' # No broadcast address for IPv6

            first_addr_int = int(network.network_address) + 1
            last_addr_int = int(network.network_address) + network.num_addresses - 1

            count = last_addr_int - first_addr_int + 1

            if count <= 0:
                return {'error': "No usable hosts available in this subnet."}
            
            # Pick random integer between first and last address
            rand_ip_int = random.randint(first_addr_int, last_addr_int)

            # Convert integer to IPv6 (colon format)
            random_ip = ipaddress.IPv6Address(rand_ip_int)
        return {
            'network': str(network.network_address),
            'broadcast': broadcast,
            'random_ip': str(random_ip)
        }
    except ValueError as e:
        return {'error': str(e)}


def ExportToCSV(subnets):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Subnet Index', 'Network Address', 'Prefix Length', 'Usable Hosts'])
    for index, subnet in subnets.items():
        writer.writerow([index, subnet['network'], subnet['prefix'], subnet['hosts']])
    output.seek(0)
    return output.getvalue()



# -------------------------------
# API Routes
# -------------------------------
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        return render_template("index.html")
    
@app.route('/ipv4_calculator', methods=['POST', 'GET'])
def ipv4_calculator():
        return render_template("IPv4_subnet.html")


@app.route('/ipv6_calculator', methods=['POST', 'GET']) 
def ipv6_calculator():
        return render_template("IPv6_subnet.html")


@app.route('/randomIP', methods=['POST', 'GET'])
def randomIP():
    return render_template("random_ip.html")

@app.route('/vlsm_calculator', methods=['POST', 'GET'])
def vlsm_calculator():
    return render_template("vlsm.html")


@app.route('/api/ip_info', methods=['POST'])
def ip_info():
    data = request.json
    try:
        ip_address = data['ip_address']
        subnet_mask = data['subnet_mask']
        ip, ip_version = ValidateIP(ip_address)
        prefix = ParseSubnet(subnet_mask, ip_version)

        if ip_version == 4:
            ip_last = LastAddr(ip, prefix)
        else:
            # For IPv6, calculate last address as network address + total addresses - 1
            network = ipaddress.ip_network(f"{ip}/{prefix}", strict=False)
            last_ipv6_int = int(network.network_address) + network.num_addresses - 1
            ip_last = ipaddress.IPv6Address(last_ipv6_int)

       
        result = {
            'network_address': str(NetAddr(ip, prefix)),
            'broadcast_address': str(BroadAddr(ip, prefix)) if ip_version == 4 else 'N/A',
            'first_address': str(FirstAddr(ip, prefix)),
            'last_address': str(ip_last) 
            #'number_of_hosts': No_Of_Hosts(ip, prefix),
        }
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/IPv4subnet', methods=['POST'])
def IPv4subnet():
    data = request.json
    try:
        ip_address = data['ip_address']
        subnet_mask = data['subnet_mask']
        no_of_hosts = data['no_of_hosts']
        ip_version = data['ip_version']
       
        try:
            no_of_hosts = int(no_of_hosts)
            if no_of_hosts <=0:
                raise ValueError("Number of hosts must be a positive integer")
        except (ValueError, TypeError):
            raise ValueError("Number of hosts must be a positive integer")

        subnets = IPv4Subnet_Split(ip_address, subnet_mask, no_of_hosts, ip_version)

        return jsonify(subnets), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/subnet', methods=['POST'])
def subnet():
    data = request.json
    try:
        ip_address = data['ip_address']
        subnet_mask = data['subnet_mask']
        no_of_hosts = data['no_of_hosts']
        ip_version = data['ip_version']
        if isinstance(no_of_hosts, str) and ',' in no_of_hosts:
            host_strings = no_of_hosts.split(',')

            host_counts = []

            for hosts in host_strings:
                host_num = int(hosts)
                host_counts.append(host_num)

            no_of_hosts = host_counts
        else:
            no_of_hosts = int(no_of_hosts)

        subnets = Subnet_Split(ip_address, subnet_mask, no_of_hosts, ip_version)

        return jsonify(subnets), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/random_ip', methods=['POST'])
def random_ip():
    data = request.json

    try:
        ip_address = data['ip_address']
        subnet_mask = data['subnet_mask']
        ip_version = data.get('ip_version', 4)  # Default to IPv4 if not provided

        result = RandomIP(ip_address, subnet_mask, ip_version)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f"Server error: {str(e)}"}), 500



@app.route('/api/export_csv', methods=['POST'])
def export_csv():
    data = request.json
    try:
        subnets = data['subnets']
        csv_data = ExportToCSV(subnets)
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={"Content-Disposition": "attachment;filename=subnets.csv"}
        ), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
