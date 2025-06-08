from scapy.all import *
import time
from collections import defaultdict
import threading
import logging
from typing import Dict, Set, Optional
from .rate_limiter import RateLimiter

class DDoSMonitor:
    def __init__(self, interface: str = None, threshold: int = 100, window: int = 60, rate_limiter: Optional[RateLimiter] = None):
        self.interface = interface
        self.threshold = threshold  # Requests per second threshold
        self.window = window  # Time window in seconds
        self.is_monitoring = False
        self.ip_request_counts: Dict[str, int] = defaultdict(int)
        self.suspicious_ips: Set[str] = set()
        self.last_reset = time.time()
        self.rate_limiter = rate_limiter or RateLimiter(max_requests=threshold, time_window=window)
        self.lock = threading.Lock()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _packet_callback(self, packet):
        """Process each captured packet"""
        if IP in packet and TCP in packet:
            src_ip = packet[IP].src
            tcp = packet[TCP]
            
            # Check for SYN-only packets (potential SYN flood)
            is_syn_only = tcp.flags == 0x02  # SYN flag only
            
            with self.lock:
                self.ip_request_counts[src_ip] += 1
                
                # Check if this IP has exceeded the threshold
                if self.ip_request_counts[src_ip] > self.threshold:
                    if src_ip not in self.suspicious_ips:
                        self.suspicious_ips.add(src_ip)
                        self.logger.warning(f"Potential DDoS attack detected from {src_ip}")
                        self.logger.warning(f"Request count: {self.ip_request_counts[src_ip]} in {self.window} seconds")
                        
                        # Block the IP using rate limiter
                        if self.rate_limiter:
                            self.rate_limiter.block_ip(src_ip)
                            self.logger.info(f"IP {src_ip} has been blocked")
                
                # Log suspicious SYN-only packets
                if is_syn_only and self.ip_request_counts[src_ip] > self.threshold / 2:
                    self.logger.warning(f"Suspicious SYN-only packet from {src_ip}")

    def _reset_counts(self):
        """Reset request counts periodically"""
        while self.is_monitoring:
            time.sleep(self.window)
            current_time = time.time()
            if current_time - self.last_reset >= self.window:
                with self.lock:
                    self.ip_request_counts.clear()
                    self.last_reset = current_time
                    self.logger.info("Request counts reset")

    def start(self):
        """Start monitoring for DDoS attacks"""
        self.is_monitoring = True
        self.logger.info(f"Starting DDoS monitoring on interface {self.interface or 'default'}")
        
        # Start the reset thread
        reset_thread = threading.Thread(target=self._reset_counts)
        reset_thread.daemon = True
        reset_thread.start()
        
        # Start packet capture
        try:
            sniff(
                iface=self.interface,
                prn=self._packet_callback,
                store=0,
                stop_filter=lambda _: not self.is_monitoring
            )
        except Exception as e:
            self.logger.error(f"Error during packet capture: {str(e)}")
            self.stop()

    def stop(self):
        """Stop monitoring"""
        self.is_monitoring = False
        self.logger.info("Stopping DDoS monitoring")
        with self.lock:
            self.ip_request_counts.clear()
            self.suspicious_ips.clear()

    def get_suspicious_ips(self) -> Set[str]:
        """Get the set of suspicious IPs"""
        with self.lock:
            return self.suspicious_ips.copy()

    def get_request_counts(self) -> Dict[str, int]:
        """Get current request counts for all IPs"""
        with self.lock:
            return dict(self.ip_request_counts)

if __name__ == "__main__":
    # Example usage
    monitor = DDoSMonitor(threshold=50, window=30)
    try:
        monitor.start()
    except KeyboardInterrupt:
        monitor.stop() 