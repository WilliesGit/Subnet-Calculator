from flask import Flask, request, jsonify, Response 
import io #module to handle input/output operations
import ipaddress
import random
import re 
import math
import csv

app = Flask(__name__) #creates a Flask application instance

def ValidateIP(ip_address):
  """ Validate an IP address and return the IP objects and its version """
  try:
    ip = ipaddress.ip_address(ip_address) # Creates an IP address object
    return ip, ip.version
  except ValueError:
    raise ValueError(f"Invalid IP address: {ip_address}")
  
  
def ParseSubnet(subnet_mask, ip_version=4):
  """ Convert a subnet mask to CIDR prefix length for IPv4 or IPv6."""
  #re.match(r'^\d{1,2}$', subnet_input) is used to check if the input string consists of 1 or 2 digits only, with no other characters. ^ (is the starting point), d (represents digits 0-9) and $ (is the end point)

  if ip_version == 4:
    #Checks for CIDR notation
    if re.match(r'^\d{1,2}$', subnet_mask):
      prefix = int(subnet_mask)
      if 0 <= prefix <=32: 
        return prefix
      raise ValueError(f"IPv4 CIDR prefix must be between 0 and 32: {subnet_mask}")
    
    try:
      mask = ipaddress.IPv4Address(subnet_mask)
      return bin(int(mask)).count('1') #Converts subnet mask into into subnet prefix 
    except ValueError:
      raise ValueError(f"Invalide IPv4 subnet mask: {subnet_mask}")
    

  elif ip_version == 6:

    if re.match(r'^\d{1,3}$', subnet_mask):
      prefix = int(subnet_mask)
      if 0 <= prefix <= 128:
        return prefix
      raise ValueError(f"IPv6 CIDR prefix must be between 0 and 128: {subnet_mask}")
    raise ValueError(f"IPv6 subnet mask must be in CIDR notation 64: {subnet_mask}")
  
  raise ValueError(f"Unsupported IP version: {ip_version}")


def NetAddr(ip_address, subnet_mask):
  """ Returns the network address for a given IP address and subnet mask."""
  interface = ipaddress.ip_interface(f"{ip_address}/{subnet_mask}") 
  return interface.network.network_address

  

def BroadAddr(ip_address, subnet_mask):
  """ Returns the broadcast address for a given IP address and subnet mask."""
  interface = ipaddress.ip_interface(f"{ip_address}/{subnet_mask}")
  return interface.network.broadcast_address
  


def FirstAddr(ip_address, subnet_mask):
  """ Returns the first usable IP address in a subnet."""
  interface = ipaddress.ip_interface(f"{ip_address}/{subnet_mask}")
  return next(interface.network.hosts(), None) #hosts() returns an iterator of usable hosts. (next) returns the first usable host


def LastAddr(ip_address, subnet_mask):
  """ Returns the last usable IP address in a subnet."""
  interface = ipaddress.ip_interface(f"{ip_address}/{subnet_mask}")
  network = interface.network

  num_hosts = network.num_addresses - 2 #Subtract network and Broadcast addresses

  if num_hosts <= 0: #If there are no usable hosts, return None
    return None
  
  last_host = ipaddress.ip_address(int(network.network_address) + num_hosts) # Calculates the last usable host by adding the number of addresses to the network address
  return last_host
  


def No_Of_Hosts(ip_address, subnet_mask):
  """ Returns the number of usable hosts in a subnet."""
  interface = ipaddress.ip_interface(f"{ip_address}/{subnet_mask}")
  return interface.network.num_addresses - 2 #Subtracts the Network and Broadcast address



def Find_Prefix(hosts, ip_version=4):
  """Finds the smallest prefix that can accommodate the required number of hosts."""
  if hosts < 0:
    raise ValueError("Number of hosts must be non-negative")
  
  total_bits = 32 if ip_version == 4 else 128 # Sets total: 32 for IPv4 and 128 for IPv6

  needed_addresses = hosts + 2 # Adds 2 for network and broadcast addresses

  # Calculate the number of bits needed to represent the required number of hosts
  if needed_addresses > 0:
    bits_for_addresses = math.ceil(math.log2(needed_addresses)) #if 60hosts is required, log2(60) = 5.91, so we round it up to 6 bits

  else:
    bits_for_addresses = 0

  prefix = total_bits - bits_for_addresses #Total bits 32 or 128 minus bits needed for addresses (e.g. 32 - 6 = 26 for IPv4) new prefix
  if prefix < 0:
    raise ValueError(f"Too many hosts ({hosts}) for IPv{ip_version}")
  
  return prefix


def Subnet_Split(ip_address, subnet_mask, no_of_hosts, ip_version=4):
  """
  Split a network into subnets that can accommodate the specified number of hosts"""

  network = ipaddress.ip_network(f"{ip_address}/{subnet_mask}", strict=False)
  ip_version = network.version 
  subnets = {} # Dictionary to hold subnets with their prefix lengths
  display_limit = 10 #Shows only the first 10 subnets
  max_subnets = 1000 if ip_version == 6 else float('inf') # Maximum number of subnets to display. inf stands for infinity display for IPv4
  
  #Checks if input is a single number (fixed-length) or list (VLSM)
  try:
    
    if isinstance(no_of_hosts, int):
      new_prefix = Find_Prefix(no_of_hosts, ip_version)
      # Fixed-length subnetting
      if new_prefix < network.prefixlen: # Check if the new prefix is greater than or equal to the original prefix
        raise ValueError(f"New prefix {new_prefix} must be greater than or equal to the original prefix {network.prefixlen}")

      subnets_prefix = network.subnets(new_prefix=new_prefix) #Generates subnets with the new prefix length

      #Loops through the subnets and stores detials in the dictionary
      for index, subnet in enumerate(subnets_prefix, start=1): 
        subnets[index] = {
          'network': str(subnet.network_address),
          'prefix': subnet.prefixlen,
          'hosts': subnet.num_addresses - 2  # Subtracts network and broadcast addresses
        }

        #Prints only the first 10 subnets
        if index <= display_limit: 
          print(f"Subnet {index}: {subnet.network_address}/{subnet.prefixlen} - Usable Hosts: {subnet.num_addresses - 2}")

        # After 10 subnets, show total number of possible subnets
        if index == display_limit + 1:
          total_subnets = 2 ** (new_prefix - network.prefixlen)
          print(f"\nTotal number of subnets: {total_subnets}") 

        # Stop after 1000 subnets for IPv6 to avoid excessive processing
        if index >= max_subnets:
          print(f"Stopped at {max_subnets} subnets to avoid excessive processing.")
          break


    elif isinstance(no_of_hosts, list):
      #VLSM: Sorts the host counts in descending order for efficient subnetting
      host_counts = sorted(no_of_hosts, reverse=True)
      current_network = int(network.network_address) # Start with the network's address as base address

      #Generate subnets with different host sizes
      for index, hosts in enumerate(host_counts, start=1):
        new_prefix = Find_Prefix(hosts, ip_version)
        subnet = ipaddress.ip_network(f"{ipaddress.ip_address(current_network)}/{new_prefix}", strict=False)

        #supernet_of: Returns True if the current network object is a supernet of the other network object (subnet)—that is, if the subnet fits in the original network
        if not network.supernet_of(subnet):
          raise ValueError(f"Subnet {index} ({subnet}) does not fit in {network}")
        
        # Store subnet details in the dictionary
        subnets[index] = {
          'network': str(subnet.network_address),
          'prefix': subnet.prefixlen,
          'hosts': subnet.num_addresses - 2  
        }

        if index <= display_limit: 
          print(f"Subnet {index}: {subnet.network_address}/{subnet.prefixlen} - Usable Hosts: {subnet.num_addresses - 2}")

        # Move to the next address
        current_network += subnet.num_addresses

        # Check if the next subnet can fit in the current network
        if current_network > int(network.broadcast_address):
          raise ValueError(f"Cannot fit all subnets in {network}")
        
        if index >= max_subnets:
          print(f"Stopped at {max_subnets} subnets to avoid excessive processing.")
          break


      if len(host_counts) > display_limit:
        print(f"\nTotal number of subnets requested: {len(host_counts)}")

    else:
      raise ValueError("Host input must be an integer (fixed-length) or a list (VLSM)")
    #return {'subnets': subnets, 'total': len(subnets)} # Returns a dictionary with subnets and total count
  
    print(f"\nTotal subnets created: {len(subnets)}")
  
  except ValueError as e:
    print(f"Error creating subnets: {e}")
    return {'error': str(e)}
  
  return subnets
      
      

def RandomIP(subnets, ip_version=4):
  """ Generate a random IP address from a subnet for IPv4 or IPv6. """
  
  if not subnets:
    print("No subnets available to generate a random IP address.")
    return None
  
  try:
    index = int(input(f"Enter the subnet index (1-{len(subnets)}):  ")) #Gets the index (1,2,3....)i.e the total number of subnets 
    if index not in subnets:
      print(f"Invalid subnet index: {index}. Please enter a valid index between 1 and {len(subnets)}.")
      return None
    
    subnet_info = subnets[index] #Saves the subnet information based on the index
    network = ipaddress.ip_network(f"{subnet_info['network']}/{subnet_info['prefix']}", strict=False)
    
    if network.version != ip_version:
      print(f"IP version mismatch: {network.version} vs {ip_version}")
      return None
    
    hosts = list(network.hosts()) #Gets the list of usable hosts in the subnet
    if not hosts:
      print("No usable hosts available in this subnet.")
      return None

    random_ip = random.choice(hosts) #Chooses a random IP address from the list of usable hosts
    print(f"Random IP Address from Subnet {index}: {random_ip}")
    #return str(random_ip)

    
  except ValueError as e:
    print(f"Error: {e}")
    return None
  
    

def ExportToCSV(subnets, filename="subnets.csv"):
  """ Export subnet details to a CSV file. """

  if not subnets:
    print("No subnets available to export.")
    return None
  
  try:
    with open(filename, mode='w', newline='') as subnet_file:
      writer = csv.writer(subnet_file) # Writes the CSV file
      writer.writerow(['Subnet Index', 'Network Address', 'Prefix Length', 'Usable Hosts']) # Writes the header row

      # Loops through the subnets and writes each subnet's details
      for index, subnet in subnets.items():
        writer.writerow([index, subnet['network'], subnet['prefix'], subnet['hosts']])
    print(f"Subnets exported to {filename}")

  except IOError as e:
    print(f"Error writing to file {filename}: {e}")
    return None

  

def HandleSubnetSplit(ip_address, subnet_mask, ip_version=4):
  """Handles all questions and the functions related to subnet splitting."""

  try:
     new_subnet = input("Enter number of hosts (single number for fixed-length, or comma-separated for VLSM, e.g., 100,50,20): ")

     # Check if input is a single number or list
     if ',' in new_subnet:
       host_strings = new_subnet.split(',')

       host_counts = [] # Create an empty list for integer host counts

       for hosts in host_strings:
         host_num = int(hosts)
         host_counts.append(host_num) # Convert each host count to an integer and add to the list

       subnets = Subnet_Split(ip_address, subnet_mask, host_counts, ip_version) # Gets the subnets based on the required number of hosts

     else:
        new_hosts = int(new_subnet)
        subnets = Subnet_Split(ip_address, subnet_mask, new_hosts, ip_version)


     if subnets:
       export_option = input("Do you want to export the subnets to a CSV file? (Yes/No): ").capitalize()

       if export_option == 'Yes':
         filename = input("Enter CSV filename (e.g., subnets.csv): ")
         ExportToCSV(subnets, filename) # Exports the subnets to a CSV file
       else:
         print("Subnets not exported.")

       random_ip_option = input("Do you want to generate a random IP address from the subnets? (Yes/No): ").capitalize()
       if random_ip_option == 'Yes':
         RandomIP(subnets, ip_version) # Generates a random IP address from the subnets
       else:
          print("Random IP generation skipped.")


  except ValueError as e:
    print(f"Error: {e}")
    return None



 

def main():
  print("***Welcome to the Subnet Calculator***\n")


  while(True):
    address_input = input("Please enter an IP address: ")
    subnet_input = input("Please enter the subnet mask (CIDR or dotted-decimal for IPv4): ")

    try:
      #Validate IP and get version
      ip, ip_version = ValidateIP(address_input)

      #Parse subnet mask based on IP version
      prefix = ParseSubnet(subnet_input, ip_version)

    
    except ValueError as e:
      print(f"Error: {e}\n1")
      

    else:
      while(True):
        print("\n")
        print("1. Network Address")
        print("2. Broadcast Address")
        print("3. First Address")
        print("4. Last Address")
        print("5. No. Usable of Hosts")
        print("6. Subnets")
        print("q. To quit")

        option = input("\nPlease select an option: ")

        if option == '1':
          result = NetAddr(ip, prefix)
          print(result)
        

        elif option == '2':
          result = BroadAddr(ip, prefix)
          print(result)
          

        elif option == '3':
          result = FirstAddr(ip, prefix)
          print(result)
          

        elif option == '4':
          result = LastAddr(ip, prefix)
          print(result)
          

        elif option == '5':
          result = No_Of_Hosts(ip, prefix)
          print(result)

        elif option == '6':
          result = HandleSubnetSplit(ip, prefix, ip_version)
          print(result)


        elif option == "q":
          return

        else:
          print("Invalid input. Try again")


        
if __name__ == "__main__":
  main()
  
