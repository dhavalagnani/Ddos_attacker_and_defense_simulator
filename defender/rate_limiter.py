import time
from collections import defaultdict
import logging
from typing import Dict, Set, Optional
import threading

class RateLimiter:
    def __init__(self, max_requests: int = 100, time_window: int = 60, block_duration: int = 300):
        self.max_requests = max_requests
        self.time_window = time_window
        self.block_duration = block_duration  # Duration in seconds to block an IP
        self.request_counts: Dict[str, int] = defaultdict(int)
        self.blocked_ips: Dict[str, float] = {}  # IP -> block_until_timestamp
        self.last_reset = time.time()
        self.lock = threading.Lock()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _reset_counts(self):
        """Reset request counts periodically"""
        while True:
            time.sleep(self.time_window)
            current_time = time.time()
            if current_time - self.last_reset >= self.time_window:
                with self.lock:
                    self.request_counts.clear()
                    self.last_reset = current_time
                    self.logger.info("Request counts reset")

    def _cleanup_expired_blocks(self):
        """Remove expired IP blocks"""
        current_time = time.time()
        with self.lock:
            expired_ips = [
                ip for ip, block_until in self.blocked_ips.items()
                if current_time >= block_until
            ]
            for ip in expired_ips:
                del self.blocked_ips[ip]
                self.logger.info(f"IP {ip} unblocked")

    def is_blocked(self, ip: str) -> bool:
        """Check if an IP is currently blocked"""
        self._cleanup_expired_blocks()
        with self.lock:
            return ip in self.blocked_ips and time.time() < self.blocked_ips[ip]

    def increment_request(self, ip: str) -> bool:
        """
        Increment request count for an IP and check if it should be blocked
        Returns True if the IP should be allowed, False if it should be blocked
        """
        if self.is_blocked(ip):
            return False

        with self.lock:
            self.request_counts[ip] += 1
            
            if self.request_counts[ip] > self.max_requests:
                self.block_ip(ip)
                return False
            
            return True

    def block_ip(self, ip: str, duration: Optional[int] = None):
        """Block an IP address for the specified duration"""
        block_until = time.time() + (duration or self.block_duration)
        with self.lock:
            self.blocked_ips[ip] = block_until
            self.logger.warning(f"IP {ip} blocked until {time.ctime(block_until)}")

    def unblock_ip(self, ip: str):
        """Manually unblock an IP address"""
        with self.lock:
            if ip in self.blocked_ips:
                del self.blocked_ips[ip]
                self.logger.info(f"IP {ip} manually unblocked")

    def get_blocked_ips(self) -> Set[str]:
        """Get the set of currently blocked IPs"""
        self._cleanup_expired_blocks()
        with self.lock:
            return set(self.blocked_ips.keys())

    def get_request_counts(self) -> Dict[str, int]:
        """Get current request counts for all IPs"""
        with self.lock:
            return dict(self.request_counts)

if __name__ == "__main__":
    # Example usage
    limiter = RateLimiter(max_requests=50, time_window=30, block_duration=60)
    
    # Start the reset thread
    reset_thread = threading.Thread(target=limiter._reset_counts, daemon=True)
    reset_thread.start()
    
    # Test the rate limiter
    test_ip = "192.168.1.1"
    for i in range(60):
        if limiter.increment_request(test_ip):
            print(f"Request {i+1} allowed")
        else:
            print(f"Request {i+1} blocked")
        time.sleep(0.1) 