import socket
import sys
import threading
from datetime import datetime


def scan_port(target_host, port, open_ports, lock):
    """
    Attempts to connect to ONE port and records it if open.
    """

    # This used to be inline inside a single big try/except that wrapped
    # the whole for-loop. That meant one bad port (timeout, refused
    # connection, etc.) could raise an exception that killed the ENTIRE
    # scan before the other ports were even checked. Wrapping the
    # try/except around just this one port means a failure here only
    # affects this port -- the loop keeps going for the rest.
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)

        result = s.connect_ex((target_host, port))

        if result == 0:
            print(f"[+] Port {port} is OPEN")
            # 'lock' prevents two threads from writing to open_ports
            # at the exact same time and corrupting the list.
            with lock:
                open_ports.append(port)
        else:
            print(f"[-] Port {port} is CLOSED")

        s.close()

    except socket.timeout:
        print(f"[-] Port {port} TIMED OUT (likely filtered by a firewall)")
    except socket.gaierror:
        print(f"[!] Could not resolve hostname while checking port {port}")
    except socket.error as e:
        print(f"[-] Port {port} error: {e}")


def parse_ports(port_input):
    """
    Turns user input like '80,443' or '1-1024' or a mix like
    '22,80-90,443' into a plain list of individual port numbers.
    """

    # This replaces the hardcoded ports_to_scan = [21, 22, 80, 443, 8080]
    # list, so the tool can be pointed at any range instead of only
    # the five ports you originally typed in by hand.

    ports = []
    for part in port_input.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            ports.extend(range(int(start), int(end) + 1))
        else:
            ports.append(int(part))
    return ports


def main():
    target_host = input("Enter the target IP address or hostname to scan: ")
    port_input = input("Enter ports to scan (e.g. 21,22,80,443 or 1-1024): ")
    ports_to_scan = parse_ports(port_input)

    start_time = datetime.now()

    print("\n" + "=" * 50)
    print(f" Scanning Target : {target_host}")
    print(f" Time Started    : {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50 + "\n")

    open_ports = []
    lock = threading.Lock()
    threads = []

    try:
        # Instead of scanning ports one-by-one (slow if you give it a
        # big range like 1-1024), we spin up one thread per port so
        # they all run their connection attempts at roughly the same
        # time. threading.Thread(target=..., args=...) tells Python
        # "run this function, with these arguments, on its own thread."
        for port in ports_to_scan:
            t = threading.Thread(
                target=scan_port, args=(target_host, port, open_ports, lock)
            )
            threads.append(t)
            t.start()

        # t.join() tells the main program "wait here until this thread
        # finishes" -- without it, the script could try to print the
        # final report before all the port checks are actually done.
        for t in threads:
            t.join()

    except KeyboardInterrupt:
        print("\n\n[!] Scan stopped by user. Exiting...")
        sys.exit()

    end_time = datetime.now()
    duration = end_time - start_time

    print("\n" + "=" * 50)
    print(f" Scan Complete in: {duration.total_seconds():.2f} seconds")
    print("=" * 50)

    log_filename = f"scan_report_{target_host}.txt"
    with open(log_filename, "w") as log_file:
        log_file.write("CYBERSECURITY PORT SCAN REPORT\n")
        log_file.write(f"Target Host : {target_host}\n")
        log_file.write(f"Scan Date   : {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"Duration    : {duration.total_seconds():.2f} seconds\n")
        log_file.write("-" * 30 + "\n")

        if open_ports:
            log_file.write("Open Ports Discovered:\n")
            for port in sorted(open_ports):
                log_file.write(f" - Port {port} is OPEN\n")
        else:
            log_file.write("No open ports were discovered during this scan.\n")

    print(f"\n[i] Results successfully saved to {log_filename}")


if __name__ == "__main__":
    main()
