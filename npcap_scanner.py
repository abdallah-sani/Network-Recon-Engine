import nmap
import sys
import os
from datetime import datetime


def main():
    target_host = input("Enter the target IP address or hostname to scan: ")
    port_range = "21-25,80,443,8080"

    start_time = datetime.now()

    print("\n" + "=" * 50)
    print(f" Scanning Target via Npcap Engine : {target_host}")
    print(f" Time Started                     : {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50 + "\n")

    try:
        # os.name == 'nt' means "this script is running on Windows."
        # 0riginal code always tried to patch the PATH with a
        # Windows-only folder (C:\Program Files...). On Linux or Mac
        # that path doesn't exist and isn't needed -- nmap installed
        # via apt/brew is already on PATH automatically. Wrapping this
        # in the os.name check means the script no longer assumes
        # Windows and won't waste time (or confuse someone) on other
        # operating systems.
        if os.name == "nt":
            nmap_paths = [r"C:\Program Files (x86)\Nmap", r"C:\Program Files\Nmap"]
            for path in nmap_paths:
                if os.path.exists(path) and path not in os.environ["PATH"]:
                    os.environ["PATH"] += os.pathsep + path

        nm = nmap.PortScanner()

        print("[i] Executing raw SYN Stealth Scan...")
        # -sS : SYN Stealth Scan (needs raw-socket privileges: sudo on
        #       Linux/Mac, admin + Npcap on Windows)
        # -Pn : treat host as online, skip the initial ping check
        # -sV : (added) probe open ports to identify service/version,
        #       e.g. "Apache 2.4.41" instead of just "port 80 open" --
        #       this is what lets the report say WHAT is running, not
        #       just THAT something is running.
        nm.scan(target_host, port_range, arguments="-sS -Pn -sV")

    except nmap.PortScannerError as e:
        print(f"\n[!] Nmap Execution Error: {e}")
        print("[i] Hint: Ensure Nmap is installed and added to your System PATH.")
        sys.exit()
    except KeyboardInterrupt:
        print("\n\n[!] Scan stopped by user. Exiting...")
        sys.exit()

    end_time = datetime.now()
    duration = end_time - start_time

    print("\n" + "=" * 50)
    print(f" Scan Complete in: {duration.total_seconds():.2f} seconds")
    print("=" * 50 + "\n")

    log_filename = f"nmap_report_{target_host}.txt"
    with open(log_filename, "w") as log_file:
        log_file.write("ADVANCED NPCAP / NMAP SECURITY REPORT\n")
        log_file.write(f"Target Host : {target_host}\n")
        log_file.write(f"Scan Date   : {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write("-" * 40 + "\n")

        if target_host in nm.all_hosts():
            host_state = nm[target_host].state()
            print(f"Host Status: {host_state.upper()}")
            log_file.write(f"Host Status : {host_state}\n\n")

            # Original code stopped right here -- it confirmed the
            # host was up but never actually looped through and printed
            # the per-port results nmap collected. This section adds
            # that missing piece.
            #
            # all_protocols() returns which protocols nmap actually
            # scanned (usually just 'tcp'). nm[target_host][proto] is
            # a dict keyed by port number, e.g. {80: {...}, 443: {...}}.
            for proto in nm[target_host].all_protocols():
                log_file.write(f"Protocol: {proto.upper()}\n")
                ports = sorted(nm[target_host][proto].keys())

                for port in ports:
                    port_info = nm[target_host][proto][port]
                    state = port_info["state"]
                    service = port_info.get("name", "unknown")
                    product = port_info.get("product", "")
                    version = port_info.get("version", "")

                    line = f" - Port {port}/{proto}: {state} ({service}"
                    if product:
                        line += f", {product} {version}".rstrip()
                    line += ")"

                    print(line)
                    log_file.write(line + "\n")
        else:
            print("[!] Host did not respond or is unreachable.")
            log_file.write("Host did not respond or is unreachable.\n")

    print(f"\n[i] Results successfully saved to {log_filename}")


if __name__ == "__main__":
    main()
