import socket
import subprocess
import requests

# Range of IPs to scan
start_ip = "10.110.23.4"
end_ip = "10.110.23.30"

# Convert IP to integer
def ip_to_int(ip):
    return int(''.join(['{:02x}'.format(int(x)) for x in ip.split('.')]), 16)

# Convert integer to IP
def int_to_ip(ip_int):
    return '.'.join([str((ip_int >> (i * 8)) & 0xFF) for i in range(4)][::-1])

# Check if a port is open
def is_port_open(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)  # 1 second timeout
        result = sock.connect_ex((ip, port))
        return result == 0

# Check if the host is reachable via ping
def is_pingable(ip):
    try:
        output = subprocess.check_output(['ping', '-c', '1', '-W', '1', ip])
        return "1 received" in output.decode('utf-8')
    except subprocess.CalledProcessError:
        return False

# Check if HTTP service is available
def check_http(ip):
    try:
        response = requests.get(f"http://{ip}", timeout=1)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Check if HTTPS service is available, ignoring certificate validation
def check_https(ip):
    try:
        response = requests.get(f"https://{ip}", timeout=1, verify=False)  # Ignore SSL cert validation
        return response.status_code == 200
    except requests.RequestException:
        return False

# Main scanning function
def scan_ip_range(start_ip, end_ip):
    start_int = ip_to_int(start_ip)
    end_int = ip_to_int(end_ip)

    results = []

    for ip_int in range(start_int, end_int + 1):
        ip = int_to_ip(ip_int)
        print(f"Scanning {ip}...")
        
        pingable = is_pingable(ip)
        ssh_open = is_port_open(ip, 22)
        http_open = is_port_open(ip, 80)
        https_open = is_port_open(ip, 443)
        http_works = check_http(ip)
        https_works = check_https(ip)
        
        result = {
            'ip': ip,
            'pingable': pingable,
            'ssh_open': ssh_open,
            'http_open': http_open,
            'https_open': https_open,
            'http_works': http_works,
            'https_works': https_works
        }

        results.append(result)
    
    return results

# Execute the scan
scan_results = scan_ip_range(start_ip, end_ip)

# Print results
for result in scan_results:
    print(f"IP: {result['ip']}")
    print(f"  Pingable: {'Yes' if result['pingable'] else 'No'}")
    print(f"  SSH Open: {'Yes' if result['ssh_open'] else 'No'}")
    print(f"  HTTP Open: {'Yes' if result['http_open'] else 'No'}")
    print(f"  HTTPS Open: {'Yes' if result['https_open'] else 'No'}")
    print(f"  HTTP Works: {'Yes' if result['http_works'] else 'No'}")
    print(f"  HTTPS Works: {'Yes' if result['https_works'] else 'No'}")
    print()
