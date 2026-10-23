
from datetime import datetime

from network_monitor.availability import load_availability_history


def test_online_device_has_online_status(tmp_path):
    log_file = tmp_path / "events.log"
    log_file.write_text(
        "[2026-10-23 10:00:00] DEVICE ONLINE: 192.168.1.10\n",
        encoding="utf-8",
    )

    result = load_availability_history(
        log_file,
        now=datetime(2026, 10, 23, 10, 5, 0),
    )

    assert len(result) == 1
    assert result[0]["ip_address"] == "192.168.1.10"
    assert result[0]["current_status"] == "ONLINE"
    assert result[0]["online_seconds"] == 0
    assert result[0]["online_hours"] == 0


def test_offline_event_records_outage(tmp_path):
    log_file = tmp_path / "events.log"
    log_file.write_text(
        "[2026-10-23 10:00:00] DEVICE ONLINE: 192.168.1.10\n"
        "[2026-10-23 10:01:00] DEVICE OFFLINE: 192.168.1.10\n",
        encoding="utf-8",
    )

    result = load_availability_history(
        log_file,
        now=datetime(2026, 10, 23, 10, 3, 0),
    )

    device = result[0]
    assert device["current_status"] == "OFFLINE"
    assert device["recorded_outages"] == 1
    assert device["online_seconds"] == 60
    assert device["outage_hours"] == 0


def test_missing_log_returns_empty_history(tmp_path):
    result = load_availability_history(tmp_path / "missing.log")
    assert result == []


def test_new_device_is_tracked(tmp_path):
    log_file = tmp_path / "events.log"
    log_file.write_text(
        "[2026-10-23 10:00:00] NEW DEVICE DETECTED: 192.168.1.20\n",
        encoding="utf-8",
    )

    result = load_availability_history(
        log_file,
        now=datetime(2026, 10, 23, 10, 2, 0),
    )

    assert len(result) == 1
    assert result[0]["ip_address"] == "192.168.1.20"
    assert result[0]["current_status"] == "ONLINE"
    assert result[0]["online_seconds"] == 0


def test_device_recovery_records_outage_duration(tmp_path):
    log_file = tmp_path / "events.log"
    log_file.write_text(
        "[2026-10-23 10:00:00] DEVICE ONLINE: 192.168.1.10\n"
        "[2026-10-23 10:01:00] DEVICE OFFLINE: 192.168.1.10\n"
        "[2026-10-23 10:03:00] DEVICE ONLINE: 192.168.1.10\n",
        encoding="utf-8",
    )

    result = load_availability_history(
        log_file,
        now=datetime(2026, 10, 23, 10, 4, 0),
    )

    device = result[0]
    assert device["current_status"] == "ONLINE"
    assert device["recorded_outages"] == 1
    assert device["online_seconds"] == 60
    assert device["outage_hours"] == 0.03


def test_repeated_offline_events_do_not_count_extra_outages(tmp_path):
    log_file = tmp_path / "events.log"
    log_file.write_text(
        "[2026-10-23 10:00:00] DEVICE ONLINE: 192.168.1.10\n"
        "[2026-10-23 10:01:00] DEVICE OFFLINE: 192.168.1.10\n"
        "[2026-10-23 10:02:00] DEVICE OFFLINE: 192.168.1.10\n",
        encoding="utf-8",
    )

    result = load_availability_history(
        log_file,
        now=datetime(2026, 10, 23, 10, 3, 0),
    )

    device = result[0]
    assert device["current_status"] == "OFFLINE"
    assert device["recorded_outages"] == 1
    assert device["online_seconds"] == 60
    assert device["outage_hours"] == 0.02
