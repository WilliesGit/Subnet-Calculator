#Input an IP + CIDR Notation, Calculate 
#i. Network Address ii. Broadcast Address iii. First/Last Usable IP iv. Number of 

"""Ip Address Module Classes

ipaddress.ip_address(address) → Creates an IPv4 or IPv6 address object.

ipaddress.ip_network(address, strict=True) → Creates an IPv4 or IPv6 network object.

ipaddress.ip_interface(address) → Creates an IPv4 or IPv6 interface object.
"""

import ipaddress
import random

def ToBinary(ip_address): #Function to convert IP address and Subnet Mask to Binary
  parts = ip_address.split('.')

  binary_parts = []

  for part in parts:
    address = format(int(part), '08b') #Binary conversion 8 = for 08 bits placement and b = for  base 2 conversion
    binary_parts.append(address)

  binary_ip = '.'.join(binary_parts)
  return binary_ip



def NetAddr(ip_address, subnet_mask):
  """
  address = ToBinary(ip_address).split('.')
  subnet = ToBinary(subnet_mask).split('.')


  network_parts = []

  for ip , subnet in zip(address, subnet): # zip This takes two lists — ip_parts and subnet_parts — and pairs up their elements.
    network = int(ip, 2) & int(subnet, 2) # 2 stands for binary representation. & is a Bitwise AND operator
    #network_parts.append(format(network, '08b')) # This returns the result in its binary equivalent 
    network_parts.append(str(network))  # This returns the result in its dotted decimal ip format

  network_address = '.'.join(network_parts)

  return network_address

  """
  interface = ipaddress.ip_interface(f"{ip_address}/{subnet_mask}") 

  return interface.network.network_address

  

  


def BroadAddr(ip_address, subnet_mask):
  """ 
  net_parts = ToBinary(NetAddr(ip_address, subnet_mask)).split('.')
  sub_parts = ToBinary(subnet_mask).split('.')

  broadcast_part = []

  for net, sub in zip(net_parts, sub_parts):
    wildcard = 255 - int(sub, 2) #Substrating 255 inverts the result (from 255.255.255.0 to 0.0.0.255) Convert the subnet octet to decimal an
    broadcast = int(net, 2) | wildcard # (|) stands for OR bitwise operator. Carrying out an OR comparisons. This sets all host bits to 1
    broadcast_part.append(str(broadcast))

  broadcast_addr = '.'.join(broadcast_part) 

  return broadcast_addr

  """
  interface = ipaddress.ip_interface(f"{ip_address}/{subnet_mask}")

  return interface.network.broadcast_address
  


def FirstAddr(ip_address, subnet_mask):
  interface = ipaddress.ip_interface(f"{ip_address}/{subnet_mask}")

  return next(interface.network.hosts()) #hosts() returns an iterator of usable hosts. (next) returns the first usable host


def LastAddr(ip_address, subnet_mask):
  interface = ipaddress.ip_interface(f"{ip_address}/{subnet_mask}")

  return str(list(interface.network.hosts())[-1]) #Converting to string to get the last item on the list returns the first usable host


def No_Of_Hosts(ip_address, subnet_mask):
  interface = ipaddress.ip_interface(f"{ip_address}/{subnet_mask}")

  return str(len(list(interface.network.hosts())))#Converting to string to get the last item on the list returns the first usable host
  
def Find_Prefix(hosts):
  """Finds the smallest prefix that can accommodate the required number of hosts."""
  host_bits = 0

  while (2 ** host_bits) - 2 < hosts:
    host_bits += 1

  return 32 - host_bits # Subnet prefix. 32 stands for the largest prefix which gives you 1 number of host

def Subnet_Split(ip_address, subnet_mask, no_of_hosts):
  network = ipaddress.ip_network(f"{ip_address}/{subnet_mask}", strict=False)

  new_prefix = Find_Prefix(no_of_hosts)

  subnets = list(network.subnets(new_prefix=new_prefix))

  print(" \nTotal number of subnet:", len(subnets))

  return subnets

def RandomIP():
  option = input("Do you wish to generate a random ip address (Yes or No): ").capitalize()
  
  if option == 'Yes':
    ip_address = input("Please enter the subnet ip address: ")
    subnet_mask = input("Please enter the CIDR: ")

    network = ipaddress.ip_network(f"{ip_address}/{subnet_mask}", strict=False)
    random_ip = random.choice(list(network.hosts()))
    print("Random IP Address: ",random_ip)

  elif option == 'No':
    return
  
  else:
        print("Invalid input. Please type 'Yes' or 'No'.")

 


def main():
  print("***Welcome to the Subnet Calculator***\n")


  while(True):
    address_input = input("Please enter an IP address: ")
    subnet_input = input("Please enter the subnet mask: ")


    try:
      ipaddress.ip_address(address_input)
      ipaddress.IPv4Interface(f"0.0.0.0/{subnet_input}") #Checks for a valid ip address
    
    except ValueError:
      print(f"Invalid ip address or subnet mask: {address_input} {subnet_input}\n1")
      
    
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
          result = NetAddr(address_input,subnet_input)
          print(result)
        

        elif option == '2':
          result = BroadAddr(address_input, subnet_input)
          print(result)
          

        elif option == '3':
          result = FirstAddr(address_input, subnet_input)
          print(result)
          

        elif option == '4':
          result = LastAddr(address_input, subnet_input)
          print(result)
          

        elif option == '5':
          result = No_Of_Hosts(address_input, subnet_input)
          print(result)

        elif option == '6':
          new_subnet = int(input("Enter the required number of hosts: "))
          result = Subnet_Split(address_input, subnet_input, new_subnet)
          for i, sub in enumerate(result, start=1):
            print(F"Subnet {i}: {sub}")
            
          RandomIP()

        elif option == "q":
          return

        else:
          print("Invalid input. Try again")


        





  #Creating an object of the ip address
  #ip_address = ipaddress.ip_network(address_input)
  
  #print(ip_address.broadcast_address)
  #NetAddr(ip_address)

if __name__ == "__main__":
  main()
  


"""

def RandomIP(subnets, ip_version=4):
  # Generate a random IP address from a subnet for IPv4 or IPv6. 
  
  option = input("Do you wish to generate a random ip address (Yes or No): ").capitalize()
  
  if option == 'Yes':
    ip_address = input("Please enter the subnet ip address: ")
    subnet_mask = input("Please enter the subnet mask (CIDR or dotted-decimal for IPv4) : ")
    try:
      #Validate IP and get version
      ip, ip_version = ValidateIP(ip_address)

      #Parse subnet mask based on IP version
      prefix = ParseSubnet(subnet_mask, ip_version)
    except ValueError as e:
      print(f"Error: {e}")
      return
    
    try:
      #Generate random IP address
      network = ipaddress.ip_network(f"{ip}/{prefix}", strict=False)

      if network.version != ip_version:
        raise ValueError(f"IP version mismatch: {network.version} vs {ip_version}")
      
      hosts = list(network.hosts())

      if not hosts:
        print("No usable hosts available in this subnet.")
        return None
      
      random_ip = random.choice(hosts)
      print("Random IP Address: ", random_ip)
      return random_ip
    
    except ValueError as e:
      print(f"Error generating random IP: {e}")
      return None 

  elif option == 'No':
    return
  
  else:
        print("Invalid input. Please type 'Yes' or 'No'.")


Keyword arguments:
argument -- description
Return: return_description
"""





