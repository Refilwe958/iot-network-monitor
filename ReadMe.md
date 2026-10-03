# IoT Network Monitor

A Python-based local network monitoring system designed to discover devices, test network connectivity, collect device information, and provide a foundation for an IoT network monitoring platform.

## Project Status

**Current milestone:** Milestone 1 — Network Discovery

### Objectives

* Discover active devices on a local IPv4 network
* Identify device IP addresses
* Retrieve MAC addresses from the local ARP table where available
* Test device reachability using ICMP
* Record network discovery results
* Build a foundation for ESP32-based IoT monitoring

## System Architecture

```text
                 Wi-Fi Router
                      |
        +-------------+-------------+
        |             |             |
      Laptop        Phone         ESP32
        |
        |
  Python Network Monitor
        |
  +-----+----------------+
  |                      |
Network Scanner       ARP Table
  |                      |
  +----------+-----------+
             |
        CSV Results
```

## Technologies

* Python
* IPv4 networking
* ICMP
* ARP
* TCP/IP networking concepts
* CSV data logging
* Git/GitHub

## Current Features

### Milestone 1

* Automatic local IP detection
* Local `/24` network discovery
* Concurrent host scanning
* ICMP connectivity testing
* ARP table parsing
* IP and MAC address reporting
* CSV result logging

## Project Structure

```text
iot-network-monitor/
│
├── network_monitor/
│   ├── __init__.py
│   └── scanner.py
│
├── data/
│
├── tests/
│
├── main.py
├── README.md
├── requirements.txt
└── .gitignore
```

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/iot-network-monitor.git
```

Enter the project directory:

```bash
cd iot-network-monitor
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Run the network monitor:

```bash
python main.py
```

## Example Output

```text
============================================================
        IoT NETWORK MONITOR - MILESTONE 1
============================================================

Local IP address: 192.168.1.105
Network detected: 192.168.1.0/24

Scanning network...
Hosts to check: 254

[ONLINE]  192.168.1.1
[ONLINE]  192.168.1.102
[ONLINE]  192.168.1.105

DISCOVERED DEVICES

IP ADDRESS        MAC ADDRESS         STATUS
------------------------------------------------------------
192.168.1.1       XX-XX-XX-XX-XX-XX   ONLINE
192.168.1.102     XX-XX-XX-XX-XX-XX   ONLINE
192.168.1.105     XX-XX-XX-XX-XX-XX   ONLINE
```

## Limitations

The current version:

* Assumes a `/24` IPv4 network
* Uses ICMP responses for basic reachability
* Relies on the operating system ARP table for MAC addresses
* May not identify devices that block ICMP
* Does not yet identify device manufacturers
* Does not yet monitor bandwidth or packet traffic
* Does not yet provide a graphical dashboard

## Planned Development

### Milestone 1 — Network Discovery

* [x] Local IP detection
* [x] Host discovery
* [x] ICMP reachability
* [x] ARP-based MAC discovery
* [x] CSV logging

### Milestone 2 — ESP32 IoT Node

* [ ] ESP32 Wi-Fi connection
* [ ] Sensor data collection
* [ ] MQTT communication
* [ ] Device heartbeat

### Milestone 3 — Network Monitoring

* [ ] Continuous device monitoring
* [ ] Latency monitoring
* [ ] Packet-loss monitoring
* [ ] Device state changes
* [ ] Network event logging

### Milestone 4 — Dashboard

* [ ] Web dashboard
* [ ] Device table
* [ ] Network statistics
* [ ] Sensor data visualization
* [ ] Alerts

### Milestone 5 — Packet Analysis

* [ ] Wireshark packet capture
* [ ] MQTT traffic analysis
* [ ] TCP/UDP analysis
* [ ] DNS analysis
* [ ] Network performance analysis

## Engineering Skills Demonstrated

This project demonstrates practical experience with:

* Computer networking
* IPv4 addressing
* Subnetting
* ICMP
* ARP
* Network monitoring
* Python programming
* Data logging
* IoT communication
* Embedded networking
* Technical documentation

## Disclaimer

This project is intended for monitoring networks that you own or are authorized to test.
