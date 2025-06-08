# DDoS Simulator

A Python-based DDoS attack simulator for educational and testing purposes. This project demonstrates various DDoS attack vectors and defense mechanisms in a controlled environment.

## ⚠️ Warning

This tool is for educational purposes only. Do not use it against any systems without explicit permission. Unauthorized use of this tool against systems is illegal and unethical.

## Features

- HTTP Flood Attack Simulation
- SYN Flood Attack Simulation
- DDoS Attack Monitoring
- Rate Limiting and IP Blocking
- Command-line Interface
- GUI Interface with real-time monitoring
- Test Mode for safe demonstrations
- Request logging and analysis
- Defense Simulation and Testing

## Requirements

- Python 3.8+
- Required packages (see requirements.txt):
  - requests
  - scapy
  - urllib3
  - flask
  - argparse
  - tkinter (included with Python installation)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/ddos-simulator.git
cd ddos-simulator
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

Note: tkinter is included with Python installation

- Windows: Python installer includes tkinter
- Linux: Install python3-tk package
- macOS: Python installer includes tkinter

## Quick Start

1. Start a local test server:

```bash
python -m http.server 8000
```

2. Run the simulator using one of these methods:

### GUI Interface (Recommended)

```bash
python interface/gui.py
```

Then in the GUI:

- Target: `http://localhost:8000`
- Threads: 5 (default)
- Duration: 30 seconds (default)
- Enable "Test Mode"
- Click "Start Attack"

### Command Line Interface

```bash
# HTTP Flood attack
python interface/cli.py http http://localhost:8000 -t 5 -d 30

# SYN Flood attack
python interface/cli.py syn 127.0.0.1 -p 8000 -t 5 -d 30

# Start monitoring
python interface/cli.py monitor -t 50 -w 30
```

### Python API

```python
from simulator import DDoSSimulator

# Create simulator instance
simulator = DDoSSimulator()

# Start monitoring
simulator.start_monitoring(threshold=50, window=30)

# Start an HTTP flood attack
simulator.start_http_flood(
    target_url="http://localhost:8000",
    num_threads=5,
    duration=30
)
```

## Project Structure

```
DDoS-Simulator/
│
├── attacker/
│   ├── http_flood.py    # HTTP flood attack implementation
│   └── syn_flood.py     # SYN flood attack implementation
│
├── defender/
│   ├── monitor.py       # DDoS attack monitoring
│   └── rate_limiter.py  # Rate limiting and IP blocking
│
├── interface/
│   ├── cli.py          # Command-line interface
│   └── gui.py          # Graphical user interface
│
├── logs/               # Attack logs directory
├── requirements.txt    # Project dependencies
├── simulator.py       # Main simulator implementation
└── README.md         # Project documentation
```

## Features in Detail

### HTTP Flood Attack

- Multi-threaded request generation
- Configurable number of threads and duration
- Test mode with request limiting
- Request logging to CSV
- Random user agents

### SYN Flood Attack

- Raw socket-based SYN packet generation
- Random source IPs and ports
- Configurable attack parameters

### DDoS Monitoring

- Real-time packet capture
- IP-based request rate tracking
- Suspicious IP detection
- Automatic IP blocking
- Thread-safe implementation

### Rate Limiting

- IP-based rate limiting
- Configurable thresholds
- Automatic IP blocking
- Block duration management

### GUI Features

- Real-time attack monitoring
- Live log display
- Blocked IPs list
- Test mode toggle
- Attack configuration
- Monitoring controls

## Defense Simulation

The simulator includes comprehensive defense mechanisms that can be tested and configured:

### 1. Attack Detection

- Real-time packet analysis
- Request rate monitoring per IP
- SYN flood detection
- HTTP flood detection
- Anomaly detection based on:
  - Request frequency
  - Packet patterns
  - Connection behavior

### 2. Rate Limiting

- Configurable request thresholds
- Time-based rate limiting
- IP-based request counting
- Automatic threshold adjustment
- Customizable time windows

### 3. IP Blocking

- Automatic IP blocking
- Configurable block duration
- Manual IP unblocking
- Block list management
- Block expiration handling

### 4. Monitoring and Logging

- Real-time attack monitoring
- Detailed request logging
- IP-based statistics
- Attack pattern analysis
- CSV export of attack data

### 5. Defense Testing

To test the defense mechanisms:

1. Start the monitoring system:

```bash
python interface/cli.py monitor -t 50 -w 30
```

2. Configure defense parameters:

- Set request threshold
- Set time window
- Configure block duration
- Enable/disable automatic blocking

3. Launch a test attack:

```bash
python interface/cli.py http http://localhost:8000 -t 5 -d 30
```

4. Monitor the defense response:

- Watch for IP blocks
- Check request rates
- Analyze attack patterns
- Review defense logs

### 6. Defense Metrics

The simulator tracks various defense metrics:

- Number of blocked IPs
- Request rates per IP
- Attack detection time
- False positive rate
- Block effectiveness
- System resource usage

## Testing

For testing purposes, you can use Python's built-in HTTP server:

```bash
python -m http.server 8000
```

This will create a test server at `http://localhost:8000` that you can use as a target.

## Logging

The simulator creates detailed logs:

- Console output for real-time monitoring
- CSV logs for request analysis
- GUI log display
- Blocked IPs tracking

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This tool is for educational purposes only. The authors are not responsible for any misuse or damage caused by this program.
