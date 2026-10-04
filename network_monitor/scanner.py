import csv
import platform
import re
import socket
import subprocess
import time
import ipaddress

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path


def get_network_configuration():
    """
    Determine the local IPv4 address and subnet mask.

    Returns:
        tuple: (local_ip, subnet_mask)
    """

    system = platform.system().lower()

    if system == "windows":
        try:
            result = subprocess.run(
                ["ipconfig"],
                capture_output=True,
                text=True,
                timeout=5
            )

            output = result.stdout

            ipv4_match = re.search(
                r"IPv4 Address[.\s]*:\s*(\d+\.\d+\.\d+\.\d+)",
                output
            )

            subnet_match = re.search(
                r"Subnet Mask[.\s]*:\s*(\d+\.\d+\.\d+\.\d+)",
                output
            )

            if ipv4_match and subnet_match:

                local_ip = ipv4_match.group(1)
                subnet_mask = subnet_match.group(1)

                return local_ip, subnet_mask

        except (subprocess.TimeoutExpired, OSError):
            pass

    # Fallback method
    try:
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        sock.connect(("8.8.8.8", 80))

        local_ip = sock.getsockname()[0]

        sock.close()

        # Common fallback mask
        return local_ip, "255.255.255.0"

    except OSError:
        return None, None


def calculate_network(local_ip, subnet_mask):
    """
    Calculate network information using IPv4 addressing.
    """

    interface = ipaddress.IPv4Interface(
        f"{local_ip}/{subnet_mask}"
    )

    network = interface.network

    return {
        "network": network,
        "network_address": str(network.network_address),
        "broadcast_address": str(network.broadcast_address),
        "subnet_mask": subnet_mask,
        "prefix_length": network.prefixlen,
        "total_addresses": network.num_addresses,
        "usable_hosts": max(network.num_addresses - 2, 0)
    }


def get_host_addresses(network):
    """
    Return all usable host addresses in the network.
    """

    return [
        str(host)
        for host in network.hosts()
    ]


def ping_host(ip_address):
    """
    Ping an IPv4 address and measure latency.

    Returns:
        tuple: (ip_address, online, latency_ms)
    """

    system = platform.system().lower()

    if system == "windows":

        command = [
            "ping",
            "-n",
            "1",
            "-w",
            "1000",
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

    start_time = time.perf_counter()

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=3
        )

        elapsed = (
            time.perf_counter() - start_time
        ) * 1000

        if result.returncode == 0:

            return (
                ip_address,
                True,
                round(elapsed, 2)
            )

        return (
            ip_address,
            False,
            None
        )

    except (
        subprocess.TimeoutExpired,
        OSError
    ):

        return (
            ip_address,
            False,
            None
        )


def get_arp_table():
    """
    Read the operating system ARP table.

    Returns:
        dictionary containing IP -> MAC mappings.
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

    except (
        subprocess.TimeoutExpired,
        OSError
    ):

        pass

    return arp_table


def scan_network(host_addresses, max_workers=50):
    """
    Scan network hosts concurrently.
    """

    discovered_devices = []

    print("\nScanning network...")
    print(f"Hosts to check: {len(host_addresses)}")
    print("-" * 70)

    with ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:

        future_to_ip = {
            executor.submit(
                ping_host,
                ip
            ): ip
            for ip in host_addresses
        }

        for future in as_completed(
            future_to_ip
        ):

            try:

                ip_address, online, latency = (
                    future.result()
                )

                if online:

                    discovered_devices.append(
                        {
                            "ip_address": ip_address,
                            "latency_ms": latency
                        }
                    )

                    print(
                        f"[ONLINE] "
                        f"{ip_address:<16} "
                        f"{latency:>7.2f} ms"
                    )

            except Exception:
                pass

    return sorted(
        discovered_devices,
        key=lambda device: tuple(
            map(
                int,
                device["ip_address"].split(".")
            )
        )
    )


def build_device_records(
    online_devices,
    arp_table
):
    """
    Build structured device records.
    """

    timestamp = datetime.now().isoformat(
        timespec="seconds"
    )

    records = []

    for device in online_devices:

        ip_address = device["ip_address"]

        records.append(
            {
                "timestamp": timestamp,
                "ip_address": ip_address,
                "mac_address": arp_table.get(
                    ip_address,
                    "Unknown"
                ),
                "latency_ms": device[
                    "latency_ms"
                ],
                "status": "ONLINE"
            }
        )

    return records


def save_results(records, output_file):
    """
    Save network results to CSV.
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
        "latency_ms",
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


def print_network_summary(
    local_ip,
    network_info,
    records
):
    """
    Display network information.
    """

    print("\n")
    print("=" * 70)
    print("                    NETWORK SUMMARY")
    print("=" * 70)

    print(f"Local IP:        {local_ip}")
    print(
        f"Subnet Mask:     "
        f"{network_info['subnet_mask']}"
    )

    print(
        f"Network:         "
        f"{network_info['network_address']}/"
        f"{network_info['prefix_length']}"
    )

    print(
        f"Broadcast:       "
        f"{network_info['broadcast_address']}"
    )

    print(
        f"Total Addresses: "
        f"{network_info['total_addresses']}"
    )

    print(
        f"Usable Hosts:    "
        f"{network_info['usable_hosts']}"
    )

    print(
        f"Online Devices:  "
        f"{len(records)}"
    )

    print("-" * 70)

    print(
        f"{'IP ADDRESS':<18}"
        f"{'MAC ADDRESS':<20}"
        f"{'LATENCY':<12}"
        f"STATUS"
    )

    print("-" * 70)

    for device in records:

        latency = device["latency_ms"]

        latency_text = (
            f"{latency:.2f} ms"
            if latency is not None
            else "N/A"
        )

        print(
            f"{device['ip_address']:<18}"
            f"{device['mac_address']:<20}"
            f"{latency_text:<12}"
            f"{device['status']}"
        )


def run_scan():

    print("=" * 70)
    print("             IoT NETWORK MONITOR")
    print("                 MILESTONE 1A")
    print("=" * 70)

    local_ip, subnet_mask = (
        get_network_configuration()
    )

    if not local_ip:

        print(
            "ERROR: Could not determine "
            "network configuration."
        )

        return

    print(
        f"\nLocal IP address: {local_ip}"
    )

    print(
        f"Subnet mask:     {subnet_mask}"
    )

    network_info = calculate_network(
        local_ip,
        subnet_mask
    )

    print(
        f"Network detected: "
        f"{network_info['network_address']}/"
        f"{network_info['prefix_length']}"
    )

    host_addresses = get_host_addresses(
        network_info["network"]
    )

    online_devices = scan_network(
        host_addresses
    )

    print("\nUpdating ARP table...")

    arp_table = get_arp_table()

    records = build_device_records(
        online_devices,
        arp_table
    )

    print_network_summary(
        local_ip,
        network_info,
        records
    )

    output_file = (
        "data/network_scan.csv"
    )

    save_results(
        records,
        output_file
    )

    print("\n" + "=" * 70)
    print("Scan complete.")
    print(
        f"Results saved to: {output_file}"
    )
    print("=" * 70)


if __name__ == "__main__":
    run_scan()
