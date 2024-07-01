import nmap

# Initialize an instance of the Nmap PortScanner
scanner = nmap.PortScanner()

# Scan the local network for connected devices using CIDR notation
scanner.scan('192.168.1.0/24')

# Iterate through each discovered host and print its details
for host in scanner.all_hosts():
    # Print the IP address and hostname (if available) of the host
    print('Host : %s (%s)' % (host, scanner[host].hostname()))
    
    # Print the MAC address of the host
    print('  MAC Address : %s' % scanner[host]['addresses']['mac'])
