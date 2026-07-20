import socket
import sys
from datetime import datetime

# 1. Capture user input and start time
target_host = input("Enter the target IP address or hostname to scan: ")
ports_to_scan = [21, 22, 80, 443, 8080]

# Record the exact moment the scan started
start_time = datetime.now()

print("\n" + "="*50)
print(f" Scanning Target : {target_host}")
print(f" Time Started    : {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
print("="*50 + "\n")

# A list to keep track of open ports for our log file later
open_ports = []

try:
    for port in ports_to_scan:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        
        result = s.connect_ex((target_host, port))
        
        if result == 0:
            print(f"[+] Port {port} is OPEN")
            open_ports.append(port)
        else:
            print(f"[-] Port {port} is CLOSED")
            
        s.close()

except socket.gaierror:
    print("\n[!] Error: Hostname could not be resolved.")
    sys.exit()

except socket.error:
    print("\n[!] Error: Could not connect to the network.")
    sys.exit()

except KeyboardInterrupt:
    print("\n\n[!] Scan stopped by user. Exiting...")
    sys.exit()

# 2. Calculate duration and handle reporting
end_time = datetime.now()
duration = end_time - start_time

print("\n" + "="*50)
print(f" Scan Complete in: {duration.total_seconds():.2f} seconds")
print("="*50)

# 3. Automatically save results to a log file
log_filename = f"scan_report_{target_host}.txt"
with open(log_filename, "w") as log_file:
    log_file.write(f"CYBERSECURITY PORT SCAN REPORT\n")
    log_file.write(f"Target Host : {target_host}\n")
    log_file.write(f"Scan Date   : {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    log_file.write(f"Duration    : {duration.total_seconds():.2f} seconds\n")
    log_file.write(f"-"*30 + "\n")
    
    if open_ports:
        log_file.write("Open Ports Discovered:\n")
        for port in open_ports:
            log_file.write(f" - Port {port} is OPEN\n")
    else:
        log_file.write("No open ports were discovered during this scan.\n")

print(f"\n[i] Results successfully saved to {log_filename}")