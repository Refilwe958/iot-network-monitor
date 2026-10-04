# IoT Network Monitor

A Python-based network monitoring tool designed to discover devices on a local network, identify the active subnet, and monitor network latency.

This project was developed as a networking portfolio project to demonstrate practical skills in **Python, TCP/IP networking, subnet detection, device discovery, and network performance monitoring**.

## Features

* Automatic local IP address detection
* Automatic subnet detection
* Local network device discovery
* IP address scanning
* Host availability checking
* Network latency monitoring
* Response-time measurement
* Command-line interface
* Clear and structured monitoring results

## Technologies Used

* **Python 3**
* Python `socket` library
* Python `ipaddress` library
* ICMP/network connectivity testing
* TCP/IP networking concepts
* IPv4 subnetting

## Project Structure

```text
iot-network-monitor/
│
├── network_monitor.py
├── README.md
├── requirements.txt
└── .gitignore
```

## How It Works

The network monitor follows these main steps:

1. Detects the computer's local IP address.
2. Determines the active network interface and subnet.
3. Calculates the local network range.
4. Scans the subnet for active devices.
5. Tests device availability.
6. Measures network response time.
7. Displays the results in the terminal.

### Example

```text
IoT Network Monitor
===================

Local IP Address: 192.168.1.10
Subnet: 192.168.1.0/24

Scanning network...

192.168.1.1    ACTIVE    2.31 ms
192.168.1.5    ACTIVE    8.74 ms
192.168.1.10   ACTIVE    0.42 ms
192.168.1.15   ACTIVE    15.62 ms

Scan complete.
```

## Subnet Detection

The application automatically determines the local network configuration instead of requiring the user to manually enter the subnet.

For example:

```text
Local IP: 192.168.1.10
Network:  192.168.1.0/24
```

This allows the monitor to adapt to different local networks.

## Latency Monitoring

The application measures the response time of devices on the network.

Latency is useful for identifying:

* Slow network responses
* Unstable connections
* Potential connectivity problems
* Devices experiencing high response times

Lower latency generally indicates a faster response between the monitoring computer and the target device.

## Installation

Clone the repository:

```bash
git clone https://github.com/Refilwe958/iot-network-monitor.git
```

Navigate into the project directory:

```bash
cd iot-network-monitor
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Run the network monitor:

```bash
python network_monitor.py
```

## Testing

The project was tested on a local network to verify:

* Local IP detection
* Subnet calculation
* Device discovery
* Host availability
* Network latency measurement
* Correct terminal output

Testing was performed using multiple devices connected to the same local network.

## Future Improvements

Planned improvements include:

* MAC address detection
* Device manufacturer identification
* Device name/hostname detection
* Continuous network monitoring
* Packet-loss monitoring
* Network performance graphs
* CSV logging
* Web-based monitoring dashboard
* IoT device classification
* Alerts for devices with high latency or packet loss

## Learning Outcomes

This project helped develop practical knowledge of:

* IPv4 addressing
* Subnetting and CIDR notation
* TCP/IP networking
* Network device discovery
* Network latency
* Python network programming
* Troubleshooting network connectivity
* Git and GitHub version control

## Author

**Refilwe Masupe**

Bachelor of Engineering Technology in Electrical Engineering

South Africa

### Portfolio Focus

Electrical Engineering | IoT | Networking | Embedded Systems | Python | Automation | Control Systems
