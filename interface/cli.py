import argparse
import sys
import logging
from typing import Optional

# Add parent directory to path to import modules
sys.path.append('..')
from attacker.http_flood import HTTPFloodAttack
from attacker.syn_flood import SYNFloodAttack
from defender.monitor import DDoSMonitor
from defender.rate_limiter import RateLimiter

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def run_http_flood(args):
    """Run HTTP flood attack"""
    logger = setup_logging()
    logger.info(f"Starting HTTP flood attack on {args.target}")
    
    attack = HTTPFloodAttack(
        target_url=args.target,
        num_threads=args.threads,
        duration=args.duration
    )
    
    try:
        attack.start()
    except KeyboardInterrupt:
        logger.info("Attack stopped by user")
        attack.stop()

def run_syn_flood(args):
    """Run SYN flood attack"""
    logger = setup_logging()
    logger.info(f"Starting SYN flood attack on {args.target}:{args.port}")
    
    attack = SYNFloodAttack(
        target_ip=args.target,
        target_port=args.port,
        num_threads=args.threads,
        duration=args.duration
    )
    
    try:
        attack.start()
    except KeyboardInterrupt:
        logger.info("Attack stopped by user")
        attack.stop()

def run_monitor(args):
    """Run DDoS monitoring"""
    logger = setup_logging()
    logger.info("Starting DDoS monitoring")
    
    monitor = DDoSMonitor(
        interface=args.interface,
        threshold=args.threshold,
        window=args.window
    )
    
    try:
        monitor.start()
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
        monitor.stop()

def main():
    parser = argparse.ArgumentParser(description='DDoS Simulator')
    subparsers = parser.add_subparsers(dest='mode', help='Operation mode')
    
    # HTTP Flood Attack
    http_parser = subparsers.add_parser('http', help='HTTP flood attack')
    http_parser.add_argument('target', help='Target URL')
    http_parser.add_argument('-t', '--threads', type=int, default=10, help='Number of attack threads')
    http_parser.add_argument('-d', '--duration', type=int, default=60, help='Attack duration in seconds')
    
    # SYN Flood Attack
    syn_parser = subparsers.add_parser('syn', help='SYN flood attack')
    syn_parser.add_argument('target', help='Target IP address')
    syn_parser.add_argument('-p', '--port', type=int, default=80, help='Target port')
    syn_parser.add_argument('-t', '--threads', type=int, default=10, help='Number of attack threads')
    syn_parser.add_argument('-d', '--duration', type=int, default=60, help='Attack duration in seconds')
    
    # Monitor Mode
    monitor_parser = subparsers.add_parser('monitor', help='DDoS monitoring')
    monitor_parser.add_argument('-i', '--interface', help='Network interface to monitor')
    monitor_parser.add_argument('-t', '--threshold', type=int, default=100, help='Request threshold per window')
    monitor_parser.add_argument('-w', '--window', type=int, default=60, help='Time window in seconds')
    
    args = parser.parse_args()
    
    if args.mode == 'http':
        run_http_flood(args)
    elif args.mode == 'syn':
        run_syn_flood(args)
    elif args.mode == 'monitor':
        run_monitor(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 