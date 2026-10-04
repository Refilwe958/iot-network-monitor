from network_monitor.performance import (
    calculate_statistics,
    classify_latency,
    calculate_packet_loss,
    generate_performance_alerts,
)


def test_calculate_statistics():
    latencies = [10, 20, 30]

    result = calculate_statistics(latencies)

    assert result["minimum_ms"] == 10
    assert result["maximum_ms"] == 30
    assert result["average_ms"] == 20


def test_empty_statistics():
    result = calculate_statistics([])

    assert result["minimum_ms"] is None
    assert result["maximum_ms"] is None
    assert result["average_ms"] is None


def test_latency_classification():
    assert classify_latency(10) == "EXCELLENT"
    assert classify_latency(30) == "GOOD"
    assert classify_latency(75) == "FAIR"
    assert classify_latency(150) == "POOR"


def test_packet_loss():
    assert calculate_packet_loss(10, 10) == 0.0
    assert calculate_packet_loss(10, 8) == 20.0
    assert calculate_packet_loss(10, 5) == 50.0


def test_performance_alerts():
    summary = {
        "average_ms": 150,
        "packet_loss": 30,
    }

    alerts = generate_performance_alerts(summary)

    assert len(alerts) == 2
    assert "High latency detected" in alerts[0]
    assert "High packet loss detected" in alerts[1]