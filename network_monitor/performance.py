import statistics
from datetime import datetime
from pathlib import Path
import csv


PERFORMANCE_FILE = Path("data/network_performance.csv")


def calculate_statistics(latencies):
    """
    Calculate basic network latency statistics.

    Parameters:
        latencies: list of latency measurements in milliseconds

    Returns:
        Dictionary containing minimum, maximum and average latency.
    """

    if not latencies:
        return {
            "minimum_ms": None,
            "maximum_ms": None,
            "average_ms": None,
        }

    return {
        "minimum_ms": round(min(latencies), 2),
        "maximum_ms": round(max(latencies), 2),
        "average_ms": round(statistics.mean(latencies), 2),
    }


def classify_latency(average_latency):
    """
    Classify network performance based on average latency.
    """

    if average_latency is None:
        return "NO DATA"

    if average_latency < 20:
        return "EXCELLENT"

    if average_latency < 50:
        return "GOOD"

    if average_latency < 100:
        return "FAIR"

    return "POOR"


def calculate_packet_loss(total_devices, online_devices):
    """
    Calculate packet loss percentage based on devices tested.
    """

    if total_devices == 0:
        return 0.0

    packet_loss = ((total_devices - online_devices) / total_devices) * 100

    return round(packet_loss, 2)


def save_performance_results(records):
    """
    Save network performance results to a CSV file.
    """

    PERFORMANCE_FILE.parent.mkdir(parents=True, exist_ok=True)

    file_exists = PERFORMANCE_FILE.exists()

    with PERFORMANCE_FILE.open(
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "timestamp",
                "ip_address",
                "latency_ms",
                "status",
            ],
        )

        if not file_exists:
            writer.writeheader()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for record in records:
            writer.writerow({
                "timestamp": timestamp,
                "ip_address": record["ip_address"],
                "latency_ms": record["latency_ms"],
                "status": record["status"],
            })

def analyze_network_performance(records):
    """
    Analyze the performance of devices discovered by the network scanner.
    """

    total_devices = len(records)

    online_devices = [
        record for record in records
        if record["status"] == "ONLINE"
    ]

    latencies = [
        record["latency_ms"]
        for record in online_devices
        if record["latency_ms"] is not None
    ]

    online_count = len(online_devices)

    statistics_result = calculate_statistics(latencies)

    packet_loss = calculate_packet_loss(
        total_devices,
        online_count
    )

    performance = classify_latency(
        statistics_result["average_ms"]
    )

    return {
        "total_devices": total_devices,
        "online_devices": online_count,
        "packet_loss": packet_loss,
        "minimum_ms": statistics_result["minimum_ms"],
        "maximum_ms": statistics_result["maximum_ms"],
        "average_ms": statistics_result["average_ms"],
        "performance": performance,
    }

def print_performance_summary(summary):
    """
    Display network performance statistics.
    """

    print()
    print("NETWORK PERFORMANCE")
    print("-------------------")

    print(f"Devices tested:   {summary['total_devices']}")
    print(f"Online devices:   {summary['online_devices']}")
    print(f"Packet loss:      {summary['packet_loss']}%")

    print()

    print(f"Minimum latency:  {summary['minimum_ms']} ms")
    print(f"Maximum latency:  {summary['maximum_ms']} ms")
    print(f"Average latency:  {summary['average_ms']} ms")

    print()

    print(f"Performance:      {summary['performance']}")       

def generate_performance_alerts(summary):
    """
    Generate alerts when network performance degrades.
    """

    alerts = []

    average_latency = summary["average_ms"]
    packet_loss = summary["packet_loss"]

    if average_latency is not None and average_latency >= 100:
        alerts.append(
            f"High latency detected: "
            f"{average_latency} ms"
        )

    if packet_loss >= 20:
        alerts.append(
            f"High packet loss detected: "
            f"{packet_loss}%"
        )

    return alerts        