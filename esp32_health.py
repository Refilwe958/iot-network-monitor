
from datetime import datetime, timezone


def check_esp32_health(
    rssi,
    last_seen,
    now=None,
    weak_signal_threshold=-75,
    stale_after_seconds=30,
):
    """
    Check ESP32 Wi-Fi signal strength and telemetry freshness.

    Parameters:
        rssi: Latest Wi-Fi signal strength in dBm, or None.
        last_seen: Datetime of the latest received telemetry message.
        now: Current datetime; injectable for predictable tests.
        weak_signal_threshold: Signals below this value are weak.
        stale_after_seconds: Maximum acceptable telemetry age.

    Returns:
        A dictionary containing health status and alert messages.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    alerts = []

    if last_seen is None:
        return {
            "status": "UNKNOWN",
            "alerts": ["No ESP32 telemetry received yet."],
            "telemetry_age_seconds": None,
        }

    # Make naive datetimes comparable with timezone-aware UTC.
    if last_seen.tzinfo is None:
        last_seen = last_seen.replace(tzinfo=timezone.utc)

    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    age_seconds = max(0, (now - last_seen).total_seconds())

    if age_seconds > stale_after_seconds:
        alerts.append(
            f"Telemetry is stale ({age_seconds:.0f} seconds old)."
        )

    if rssi is None:
        alerts.append("RSSI reading is unavailable.")
    elif rssi < weak_signal_threshold:
        alerts.append(f"Weak Wi-Fi signal: {rssi} dBm.")

    if age_seconds > stale_after_seconds:
        status = "STALE"
    elif alerts:
        status = "WARNING"
    else:
        status = "HEALTHY"

    return {
        "status": status,
        "alerts": alerts,
        "telemetry_age_seconds": round(age_seconds, 1),
    }
