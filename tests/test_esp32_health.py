
from datetime import datetime, timedelta, timezone

from esp32_health import check_esp32_health


def test_healthy_esp32():
    now = datetime.now(timezone.utc)

    result = check_esp32_health(
        rssi=-60,
        last_seen=now - timedelta(seconds=5),
        now=now,
    )

    assert result["status"] == "HEALTHY"
    assert result["alerts"] == []


def test_weak_wifi_signal():
    now = datetime.now(timezone.utc)

    result = check_esp32_health(
        rssi=-82,
        last_seen=now - timedelta(seconds=5),
        now=now,
    )

    assert result["status"] == "WARNING"
    assert any("Weak Wi-Fi signal" in alert
               for alert in result["alerts"])


def test_stale_telemetry():
    now = datetime.now(timezone.utc)

    result = check_esp32_health(
        rssi=-60,
        last_seen=now - timedelta(seconds=45),
        now=now,
    )

    assert result["status"] == "STALE"


def test_no_telemetry_received():
    result = check_esp32_health(
        rssi=None,
        last_seen=None,
    )

    assert result["status"] == "UNKNOWN"


def test_missing_rssi():
    now = datetime.now(timezone.utc)

    result = check_esp32_health(
        rssi=None,
        last_seen=now - timedelta(seconds=5),
        now=now,
    )

    assert result["status"] == "WARNING"
    assert "RSSI reading is unavailable." in result["alerts"]


def test_rssi_exactly_at_threshold():
    now = datetime.now(timezone.utc)

    result = check_esp32_health(
        rssi=-75,
        last_seen=now - timedelta(seconds=5),
        now=now,
    )

    assert result["status"] == "HEALTHY"
    assert result["alerts"] == []


def test_telemetry_exactly_at_stale_threshold():
    now = datetime.now(timezone.utc)

    result = check_esp32_health(
        rssi=-60,
        last_seen=now - timedelta(seconds=30),
        now=now,
    )

    assert result["status"] == "HEALTHY"


def test_timezone_aware_timestamps():
    now = datetime(2026, 10, 23, 12, 0, tzinfo=timezone.utc)
    last_seen = datetime(
        2026, 10, 23, 14, 0,
        tzinfo=timezone(timedelta(hours=2)),
    )

    result = check_esp32_health(
        rssi=-60,
        last_seen=last_seen,
        now=now,
    )

    assert result["status"] == "HEALTHY"
    assert result["telemetry_age_seconds"] == 0
