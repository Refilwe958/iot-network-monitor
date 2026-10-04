import time
from datetime import datetime
from pathlib import Path

from network_monitor.scanner import (
    get_network_configuration,
    calculate_network,
    get_host_addresses,
    scan_network,
    get_arp_table,
    build_device_records,
)


SCAN_INTERVAL = 30

LOG_FILE = Path("logs/network_events.log")


def log_event(message):
    """
    Save a network event to the monitoring log.
    """

    LOG_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    log_message = (
        f"[{timestamp}] {message}"
    )

    print(log_message)

    with LOG_FILE.open(
        "a",
        encoding="utf-8"
    ) as log_file:

        log_file.write(
            log_message + "\n"
        )


def get_device_ips(records):
    """
    Extract IP addresses from device records.
    """

    return {
        device["ip_address"]
        for device in records
    }


def detect_changes(previous_devices, current_devices):
    """
    Compare two network scans.

    Returns:
        new_devices
        lost_devices
    """

    new_devices = (
        current_devices - previous_devices
    )

    lost_devices = (
        previous_devices - current_devices
    )

    return new_devices, lost_devices


def run_monitor():

    print("=" * 70)
    print("              IoT NETWORK MONITOR")
    print("             CONTINUOUS MONITORING")
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

    network_info = calculate_network(
        local_ip,
        subnet_mask
    )

    host_addresses = get_host_addresses(
        network_info["network"]
    )

    print(
        f"\nLocal IP: {local_ip}"
    )

    print(
        f"Network: "
        f"{network_info['network']}"
    )

    print(
        f"Monitoring interval: "
        f"{SCAN_INTERVAL} seconds"
    )

    print("\nPress CTRL+C to stop monitoring.\n")

    previous_devices = set()

    first_scan = True

    try:

        while True:

            scan_time = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            print("\n" + "=" * 70)

            print(
                f"SCAN TIME: {scan_time}"
            )

            print("=" * 70)

            online_devices = scan_network(
                host_addresses
            )

            arp_table = get_arp_table()

            records = build_device_records(
                online_devices,
                arp_table
            )

            current_devices = (
                get_device_ips(records)
            )

            if first_scan:

                for ip_address in sorted(
                    current_devices
                ):

                    log_event(
                        f"DEVICE ONLINE: "
                        f"{ip_address}"
                    )

                first_scan = False

            else:

                new_devices, lost_devices = (
                    detect_changes(
                        previous_devices,
                        current_devices
                    )
                )

                for ip_address in sorted(
                    new_devices
                ):

                    log_event(
                        f"NEW DEVICE DETECTED: "
                        f"{ip_address}"
                    )

                for ip_address in sorted(
                    lost_devices
                ):

                    log_event(
                        f"DEVICE OFFLINE: "
                        f"{ip_address}"
                    )

                if not new_devices and not lost_devices:

                    log_event(
                        "No device changes detected."
                    )

            previous_devices = (
                current_devices
            )

            print(
                f"\nOnline devices: "
                f"{len(current_devices)}"
            )

            print(
                f"Next scan in "
                f"{SCAN_INTERVAL} seconds..."
            )

            time.sleep(SCAN_INTERVAL)

    except KeyboardInterrupt:

        print(
            "\n\nMonitoring stopped by user."
        )

        log_event(
            "NETWORK MONITOR STOPPED"
        )


if __name__ == "__main__":
    run_monitor()