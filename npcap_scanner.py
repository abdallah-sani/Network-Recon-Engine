import nmap
import sys
from datetime import datetime

# 1. Capture user input and start time
target_host = input("Enter the target IP address or hostname to scan: ")
# We'll scan a clean range of common ports using Nmap syntax
port_range = "21-25,80,443,8080"

start_time = datetime.now()

print("\n" + "="*50)
print(f" Scanning Target via Npcap Engine : {target_host}")
print(f" Time Started                     : {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
print("="*50 + "\n")

try:
    #Tell Python exactly where Nmap is installed on Windows before waking it up
    import os
    nmap_path = [r"C:\Program Files (x86)\Nmap", r"C:\Program Files\Nmap"]
    for path in nmap_path:
        if os.path.exists(path) and path not in os.environ['PATH']:
            os.environ['PATH'] += os.pathsep + path 


 
 
 
    #2. Initialize the Nmap PortScanner object
    # This object initializes the background binaries that rely on Npcap
    nm = nmap.PortScanner()
    
    print("[i] Executing raw SYN Stealth Scan...")
    # -sS: SYN Stealth Scan (Requires Npcap to craft raw packets)
    # -Pn: Treat host as online (skips discovery ping)
    nm.scan(target_host, port_range, arguments='-sS -Pn')

except nmap.PortScannerError as e:
    print(f"\n[!] Nmap Execution Error: {e}")
    print("[i] Hint: Ensure Nmap is installed and added to your System PATH.")
    sys.exit()
except KeyboardInterrupt:
    print("\n\n[!] Scan stopped by user. Exiting...")
    sys.exit()

# 3. Process and Print the Results
end_time = datetime.now()
duration = end_time - start_time

print("\n" + "="*50)
print(f" Scan Complete in: {duration.total_seconds():.2f} seconds")
print("="*50 + "\n")

# Open a text file to write the professional Npcap audit report
log_filename = f"nmap_report_{target_host}.txt"
with open(log_filename, "w") as log_file:
    log_file.write(f"ADVANCED NPCAP / NMAP SECURITY REPORT\n")
    log_file.write(f"Target Host : {target_host}\n")
    log_file.write(f"Scan Date   : {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    log_file.write(f"-"*40 + "\n")

    # Check if Nmap found any host data
    if target_host in nm.all_hosts():
        host_state = nm[target_host].state()
        print(f"Host Status: {host_state.upper()}")
        log_file.write(f"Host Status : {host_state}\n\n")
        
        # Loop through protocols discovered (e.g., tcp)
        for proto in nm[target_host].all_protocols():
            log_file.write(f"Protocol: {proto.upper()}\n")
            ports = nm[target_host][proto].keys()
            
            for port in sorted(ports):
                state = nm[target_host][proto][port]['state']
                service = nm[target_host][proto][port]['name']
                
                # Display to terminal
                print(f"[{state.upper()}] Port {port}: {service}")
                # Write to text log file
                log_file.write(f" - Port {port:<5} | State: {state:<6} | Service: {service}\n")
    else:
        print("[!] No host data returned. Target might be offline or blocking packets.")
        log_file.write("No operational host data discovered.\n")

print(f"\n[i] Npcap audit results successfully saved to {log_filename}")