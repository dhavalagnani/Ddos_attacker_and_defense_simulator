import sys
import logging
from typing import Optional
import threading
import time

from attacker.http_flood import HTTPFloodAttack
from attacker.syn_flood import SYNFloodAttack
from defender.monitor import DDoSMonitor
from defender.rate_limiter import RateLimiter

class DDoSSimulator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.monitor: Optional[DDoSMonitor] = None
        self.rate_limiter: Optional[RateLimiter] = None
        self.attack: Optional[HTTPFloodAttack | SYNFloodAttack] = None
        self.is_running = False

    def setup_logging(self):
        """Configure logging for the application"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def start_monitoring(self, interface: Optional[str] = None, threshold: int = 100, window: int = 60):
        """Start the DDoS monitoring system"""
        self.monitor = DDoSMonitor(interface=interface, threshold=threshold, window=window)
        self.rate_limiter = RateLimiter(max_requests=threshold, time_window=window)
        
        # Start monitoring in a separate thread
        monitor_thread = threading.Thread(target=self.monitor.start)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        self.logger.info("DDoS monitoring started")

    def start_http_flood(self, target_url: str, num_threads: int = 10, duration: int = 60):
        """Start an HTTP flood attack"""
        self.attack = HTTPFloodAttack(
            target_url=target_url,
            num_threads=num_threads,
            duration=duration
        )
        self.attack.start()
        self.logger.info(f"HTTP flood attack started on {target_url}")

    def start_syn_flood(self, target_ip: str, target_port: int = 80, num_threads: int = 10, duration: int = 60):
        """Start a SYN flood attack"""
        self.attack = SYNFloodAttack(
            target_ip=target_ip,
            target_port=target_port,
            num_threads=num_threads,
            duration=duration
        )
        self.attack.start()
        self.logger.info(f"SYN flood attack started on {target_ip}:{target_port}")

    def stop_attack(self):
        """Stop the current attack"""
        if self.attack:
            self.attack.stop()
            self.attack = None
            self.logger.info("Attack stopped")

    def stop_monitoring(self):
        """Stop the DDoS monitoring system"""
        if self.monitor:
            self.monitor.stop()
            self.monitor = None
            self.rate_limiter = None
            self.logger.info("DDoS monitoring stopped")

    def get_blocked_ips(self) -> set:
        """Get the list of blocked IPs"""
        if self.rate_limiter:
            return self.rate_limiter.get_blocked_ips()
        return set()

    def get_suspicious_ips(self) -> set:
        """Get the list of suspicious IPs"""
        if self.monitor:
            return self.monitor.get_suspicious_ips()
        return set()

def main():
    simulator = DDoSSimulator()
    simulator.setup_logging()
    
    # Example usage
    try:
        # Start monitoring
        simulator.start_monitoring(threshold=50, window=30)
        
        # Start an HTTP flood attack
        simulator.start_http_flood(
            target_url="http://localhost:5000",
            num_threads=5,
            duration=30
        )
        
        # Monitor for 30 seconds
        time.sleep(30)
        
        # Print blocked and suspicious IPs
        print("\nBlocked IPs:", simulator.get_blocked_ips())
        print("Suspicious IPs:", simulator.get_suspicious_ips())
        
    except KeyboardInterrupt:
        print("\nStopping simulator...")
    finally:
        simulator.stop_attack()
        simulator.stop_monitoring()

if __name__ == "__main__":
    main() 