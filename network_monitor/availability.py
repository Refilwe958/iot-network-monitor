
from datetime import datetime
from pathlib import Path
import re


EVENT_PATTERN = re.compile(
    r"^\[(?P<timestamp>\d{4}-\d{2}-\d{2} "
    r"\d{2}:\d{2}:\d{2})\]\s+(?P<message>.+)$"
)

ONLINE_PATTERN = re.compile(
    r"DEVICE ONLINE: (?P<ip>\d{1,3}(?:\.\d{1,3}){3})$"
)

NEW_DEVICE_PATTERN = re.compile(
    r"NEW DEVICE DETECTED: "
    r"(?P<ip>\d{1,3}(?:\.\d{1,3}){3})$"
)

OFFLINE_PATTERN = re.compile(
    r"DEVICE OFFLINE: (?P<ip>\d{1,3}(?:\.\d{1,3}){3})$"
)


def load_availability_history(
    log_file="logs/network_events.log",
    now=None,
):
    """Summarise device availability using recorded event intervals.

    Durations include only intervals between consecutive recorded
    status events. Time after the last event is not added because
    monitoring may have stopped.
    """

    path = Path(log_file)

    if not path.exists():
        return []

    states = {}
    summaries = {}

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            match = EVENT_PATTERN.match(line.strip())

            if not match:
                continue

            timestamp = datetime.strptime(
                match.group("timestamp"),
                "%Y-%m-%d %H:%M:%S",
            )
            message = match.group("message")

            online_match = ONLINE_PATTERN.search(message)
            new_match = NEW_DEVICE_PATTERN.search(message)
            offline_match = OFFLINE_PATTERN.search(message)

            if online_match:
                ip = online_match.group("ip")
                event = "ONLINE"
            elif new_match:
                ip = new_match.group("ip")
                event = "ONLINE"
            elif offline_match:
                ip = offline_match.group("ip")
                event = "OFFLINE"
            else:
                continue

            if ip not in summaries:
                summaries[ip] = {
                    "ip_address": ip,
                    "online_seconds": 0.0,
                    "recorded_outages": 0,
                    "completed_outage_seconds": 0.0,
                    "current_status": "UNKNOWN",
                    "last_event": None,
                    "history_complete": False,
                }

            summary = summaries[ip]
            previous = states.get(ip)

            if previous is not None:
                previous_status, previous_time = previous

                elapsed = max(
                    0.0,
                    (timestamp - previous_time).total_seconds(),
                )

                if previous_status == "ONLINE":
                    summary["online_seconds"] += elapsed
                elif previous_status == "OFFLINE":
                    summary["completed_outage_seconds"] += elapsed

            if (
                event == "OFFLINE"
                and previous is not None
                and previous[0] == "ONLINE"
            ):
                summary["recorded_outages"] += 1

            states[ip] = (event, timestamp)
            summary["current_status"] = event
            summary["last_event"] = timestamp

    for summary in summaries.values():
        summary["online_seconds"] = round(
            summary["online_seconds"], 2
        )
        summary["completed_outage_seconds"] = round(
            summary["completed_outage_seconds"], 2
        )
        summary["online_hours"] = round(
            summary["online_seconds"] / 3600, 2
        )
        summary["outage_hours"] = round(
            summary["completed_outage_seconds"] / 3600, 2
        )

    return sorted(
        summaries.values(),
        key=lambda item: item["ip_address"],
    )
