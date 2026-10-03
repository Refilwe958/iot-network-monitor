import csv
import platform
import re
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path


def get_local_ip():
    """
    Determine the computer's local IPv4 address.
    """

    hostname = socket.gethostname()

    try:
        addresses = socket.gethostbyname_ex(hostname)[2]

        for address in addresses:
            if address.startswith(("10.", "192.168.", "172.")):
                return address

    except socket.gaierror:
        pass

    # Fallback method
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        local_ip = sock.getsockname()[0]
        sock.close()
        return local_ip

    except OSError:
        return None


def create_network_range(local_ip):
    """
    Create a /24 network range from the local IP address.

    Example:
        192.168.1.25 -> 192.168.1.1 - 192.168.1.254
    """

    if not local_ip:
        raise ValueError("Could not determine local IP address.")

    parts = local_ip.split(".")

    if len(parts) != 4:
        raise ValueError("Invalid IPv4 address.")

    network_prefix = ".".join(parts[:3])

    return [
        f"{network_prefix}.{number}"
        for number in range(1, 255)
    ]


def ping_host(ip_address):
    """
    Ping one IPv4 address.

    Returns:
        True if the host responds.
        False otherwise.
    """

    system = platform.system().lower()

    if system == "windows":
        command = [
            "ping",
            "-n",
            "1",
            "-w",
            "500",
            ip_address
        ]
    else:
        command = [
            "ping",
            "-c",
            "1",
            "-W",
            "1",
            ip_address
        ]

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=2
        )

        return result.returncode == 0

    except (subprocess.TimeoutExpired, OSError):
        return False


def get_arp_table():
    """
    Read the operating system ARP table.

    Returns:
        Dictionary containing IP -> MAC mappings.
    """

    arp_table = {}

    try:
        result = subprocess.run(
            ["arp", "-a"],
            capture_output=True,
            text=True,
            timeout=5
        )

        output = result.stdout

        pattern = re.compile(
            r"(\d+\.\d+\.\d+\.\d+)\s+"
            r"([0-9a-fA-F:-]{11,17})"
        )

        for match in pattern.finditer(output):
            ip_address = match.group(1)
            mac_address = match.group(2)

            arp_table[ip_address] = mac_address

    except (subprocess.TimeoutExpired, OSError):
        pass

    return arp_table


def scan_network(network_addresses, max_workers=50):
    """
    Scan a list of IP addresses concurrently.

    Returns:
        List of discovered devices.
    """

    discovered_devices = []

    print("\nScanning network...")
    print(f"Hosts to check: {len(network_addresses)}")
    print("-" * 60)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:

        future_to_ip = {
            executor.submit(ping_host, ip): ip
            for ip in network_addresses
        }

        for future in as_completed(future_to_ip):

            ip_address = future_to_ip[future]

            try:
                is_online = future.result()

                if is_online:
                    discovered_devices.append(ip_address)
                    print(f"[ONLINE]  {ip_address}")

            except Exception:
                pass

    return sorted(
        discovered_devices,
        key=lambda ip: tuple(map(int, ip.split(".")))
    )


def build_device_records(online_devices, arp_table):
    """
    Build structured device records.
    """

    timestamp = datetime.now().isoformat(timespec="seconds")

    records = []

    for ip_address in online_devices:

        mac_address = arp_table.get(
            ip_address,
            "Unknown"
        )

        records.append(
            {
                "timestamp": timestamp,
                "ip_address": ip_address,
                "mac_address": mac_address,
                "status": "ONLINE"
            }
        )

    return records


def save_results(records, output_file):
    """
    Save scan results to CSV.
    """

    output_path = Path(output_file)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fieldnames = [
        "timestamp",
        "ip_address",
        "mac_address",
        "status"
    ]

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(records)


def run_scan():
    """
    Execute a complete network scan.
    """

    print("=" * 60)
    print("        IoT NETWORK MONITOR - MILESTONE 1")
    print("=" * 60)

    local_ip = get_local_ip()

    if not local_ip:
        print("ERROR: Could not determine local IP address.")
        return

    print(f"\nLocal IP address: {local_ip}")

    network_addresses = create_network_range(local_ip)

    network_prefix = ".".join(local_ip.split(".")[:3])

    print(f"Network detected: {network_prefix}.0/24")

    online_devices = scan_network(network_addresses)

    print("\nUpdating ARP table...")
    arp_table = get_arp_table()

    records = build_device_records(
        online_devices,
        arp_table
    )

    print("\n" + "=" * 60)
    print("DISCOVERED DEVICES")
    print("=" * 60)

    if not records:
        print("No responding devices were found.")
    else:

        print(
            f"{'IP ADDRESS':<18}"
            f"{'MAC ADDRESS':<20}"
            f"STATUS"
        )

        print("-" * 60)

        for device in records:

            print(
                f"{device['ip_address']:<18}"
                f"{device['mac_address']:<20}"
                f"{device['status']}"
            )

    output_file = "data/network_scan.csv"

    save_results(
        records,
        output_file
    )

    print("\nScan complete.")
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    run_scan()