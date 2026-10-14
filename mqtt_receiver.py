
import csv
import json
from datetime import datetime
from pathlib import Path

import paho.mqtt.client as mqtt

# MQTT broker settings
BROKER = "10.5.51.102"
PORT = 1883
TOPIC = "iot-network-monitor/esp32/status"

# CSV output file
OUTPUT_FILE = Path(__file__).parent / "data" / "esp32_telemetry.csv"

FIELDS = [
    "timestamp",
    "device",
    "status",
    "ip",
    "rssi",
    "uptime_seconds",
    "topic",
    "raw_message",
]


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f"Connected to MQTT broker at {BROKER}:{PORT}")
        client.subscribe(TOPIC)
        print(f"Subscribed to: {TOPIC}")
        print(f"Saving telemetry to: {OUTPUT_FILE}")
        print("Waiting for ESP32 messages... Press Ctrl+C to stop.")
    else:
        print(f"MQTT connection failed: {reason_code}")


def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8", errors="replace")
    print(f"Received: {payload}")

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        print("Invalid JSON received; message was not saved.")
        return

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    file_exists = OUTPUT_FILE.exists() and OUTPUT_FILE.stat().st_size > 0

    row = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "device": data.get("device", ""),
        "status": data.get("status", ""),
        "ip": data.get("ip", ""),
        "rssi": data.get("rssi", ""),
        "uptime_seconds": data.get("uptime_seconds", ""),
        "topic": msg.topic,
        "raw_message": payload,
    }

    try:
        with OUTPUT_FILE.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)

            if not file_exists:
                writer.writeheader()

            writer.writerow(row)

        print(f"Saved telemetry | RSSI: {row['rssi']} dBm | IP: {row['ip']}")
    except OSError as error:
        print(f"Could not save telemetry: {error}")


def main():
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="iot-network-monitor-python",
    )

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nStopping MQTT receiver...")
    except OSError as error:
        print(f"MQTT connection error: {error}")
        print("Check that Mosquitto is running and the broker IP is correct.")
    finally:
        client.disconnect()
        client.loop_stop()


if __name__ == "__main__":
    main()
