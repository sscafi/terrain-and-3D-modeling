import nmap

# Set up an Nmap PortScanner object
scanner = nmap.PortScanner()

# Scan the local network for connected devices
scanner.scan('192.168.1.0/24')

# Print out the IP addresses and MAC addresses of connected devices
for host in scanner.all_hosts():
    print('Host : %s (%s)' % (host, scanner[host].hostname()))
    print('  MAC Address : %s' % scanner[host]['addresses']['mac'])
