import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import logging
from typing import Optional
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from attacker.http_flood import HTTPFloodAttack
from attacker.syn_flood import SYNFloodAttack
from defender.monitor import DDoSMonitor
from defender.rate_limiter import RateLimiter

class DDoSSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DDoS Simulator")
        self.root.geometry("800x600")
        
        # Initialize components
        self.monitor: Optional[DDoSMonitor] = None
        self.attack: Optional[HTTPFloodAttack | SYNFloodAttack] = None
        
        # Create GUI elements first
        self.create_widgets()
        
        # Then setup logging
        self.setup_logging()
        
        # Start with monitoring disabled
        self.is_monitoring = False

    def setup_logging(self):
        """Configure logging to both file and GUI"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create a handler for the GUI
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                logging.Handler.__init__(self)
                self.text_widget = text_widget

            def emit(self, record):
                msg = self.format(record)
                def append():
                    self.text_widget.configure(state='normal')
                    self.text_widget.insert(tk.END, msg + '\n')
                    self.text_widget.configure(state='disabled')
                    self.text_widget.see(tk.END)
                self.text_widget.after(0, append)

        # Add the handler to the logger
        self.log_handler = TextHandler(self.log_text)
        self.log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(self.log_handler)

    def create_widgets(self):
        """Create all GUI widgets"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Attack tab
        attack_frame = ttk.Frame(notebook)
        notebook.add(attack_frame, text='Attack')
        
        # Monitor tab
        monitor_frame = ttk.Frame(notebook)
        notebook.add(monitor_frame, text='Monitor')
        
        # Create log area first
        self.create_log_area()
        
        # Create attack controls
        self.create_attack_controls(attack_frame)
        
        # Create monitor controls
        self.create_monitor_controls(monitor_frame)

    def create_attack_controls(self, parent):
        """Create attack control widgets"""
        # Target URL/IP
        ttk.Label(parent, text="Target:").grid(row=0, column=0, padx=5, pady=5)
        self.target_entry = ttk.Entry(parent, width=40)
        self.target_entry.grid(row=0, column=1, padx=5, pady=5)
        self.target_entry.insert(0, "http://localhost:8000")
        
        # Attack type
        ttk.Label(parent, text="Attack Type:").grid(row=1, column=0, padx=5, pady=5)
        self.attack_type = ttk.Combobox(parent, values=["HTTP Flood", "SYN Flood"])
        self.attack_type.grid(row=1, column=1, padx=5, pady=5)
        self.attack_type.set("HTTP Flood")
        
        # Threads
        ttk.Label(parent, text="Threads:").grid(row=2, column=0, padx=5, pady=5)
        self.threads_spinbox = ttk.Spinbox(parent, from_=1, to=100, width=10)
        self.threads_spinbox.grid(row=2, column=1, padx=5, pady=5)
        self.threads_spinbox.set(5)
        
        # Duration
        ttk.Label(parent, text="Duration (s):").grid(row=3, column=0, padx=5, pady=5)
        self.duration_spinbox = ttk.Spinbox(parent, from_=1, to=3600, width=10)
        self.duration_spinbox.grid(row=3, column=1, padx=5, pady=5)
        self.duration_spinbox.set(30)
        
        # Test mode
        self.test_mode_var = tk.BooleanVar(value=True)
        self.test_mode_check = ttk.Checkbutton(parent, text="Test Mode", variable=self.test_mode_var)
        self.test_mode_check.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        
        # Start/Stop button
        self.attack_button = ttk.Button(parent, text="Start Attack", command=self.toggle_attack)
        self.attack_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    def create_monitor_controls(self, parent):
        """Create monitoring control widgets"""
        # Interface
        ttk.Label(parent, text="Interface:").grid(row=0, column=0, padx=5, pady=5)
        self.interface_entry = ttk.Entry(parent, width=40)
        self.interface_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Threshold
        ttk.Label(parent, text="Threshold:").grid(row=1, column=0, padx=5, pady=5)
        self.threshold_spinbox = ttk.Spinbox(parent, from_=1, to=1000, width=10)
        self.threshold_spinbox.grid(row=1, column=1, padx=5, pady=5)
        self.threshold_spinbox.set(100)
        
        # Window
        ttk.Label(parent, text="Window (s):").grid(row=2, column=0, padx=5, pady=5)
        self.window_spinbox = ttk.Spinbox(parent, from_=1, to=3600, width=10)
        self.window_spinbox.grid(row=2, column=1, padx=5, pady=5)
        self.window_spinbox.set(60)
        
        # Start/Stop button
        self.monitor_button = ttk.Button(parent, text="Start Monitoring", command=self.toggle_monitoring)
        self.monitor_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        
        # Blocked IPs list
        ttk.Label(parent, text="Blocked IPs:").grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        self.blocked_ips_text = scrolledtext.ScrolledText(parent, height=10, width=50)
        self.blocked_ips_text.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    def create_log_area(self):
        """Create the logging area"""
        # Log area
        log_frame = ttk.LabelFrame(self.root, text="Logs")
        log_frame.pack(expand=True, fill='both', padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.pack(expand=True, fill='both', padx=5, pady=5)
        self.log_text.configure(state='disabled')

    def toggle_attack(self):
        """Toggle attack on/off"""
        if self.attack is None:
            # Start attack
            target = self.target_entry.get()
            threads = int(self.threads_spinbox.get())
            duration = int(self.duration_spinbox.get())
            test_mode = self.test_mode_var.get()
            
            if self.attack_type.get() == "HTTP Flood":
                self.attack = HTTPFloodAttack(
                    target_url=target,
                    num_threads=threads,
                    duration=duration,
                    test_mode=test_mode,
                    log_file="logs/http_flood_attack.csv"
                )
            else:  # SYN Flood
                self.attack = SYNFloodAttack(
                    target_ip=target,
                    target_port=80,
                    num_threads=threads,
                    duration=duration
                )
            
            self.attack.start()
            self.attack_button.configure(text="Stop Attack")
            self.logger.info("Attack started")
        else:
            # Stop attack
            self.attack.stop()
            self.attack = None
            self.attack_button.configure(text="Start Attack")
            self.logger.info("Attack stopped")

    def toggle_monitoring(self):
        """Toggle monitoring on/off"""
        if not self.is_monitoring:
            # Start monitoring
            interface = self.interface_entry.get() or None
            threshold = int(self.threshold_spinbox.get())
            window = int(self.window_spinbox.get())
            
            self.monitor = DDoSMonitor(
                interface=interface,
                threshold=threshold,
                window=window
            )
            
            # Start monitoring in a separate thread
            monitor_thread = threading.Thread(target=self.monitor.start)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            self.is_monitoring = True
            self.monitor_button.configure(text="Stop Monitoring")
            self.logger.info("Monitoring started")
            
            # Start updating blocked IPs
            self.update_blocked_ips()
        else:
            # Stop monitoring
            if self.monitor:
                self.monitor.stop()
                self.monitor = None
            self.is_monitoring = False
            self.monitor_button.configure(text="Start Monitoring")
            self.logger.info("Monitoring stopped")

    def update_blocked_ips(self):
        """Update the blocked IPs display"""
        if self.is_monitoring and self.monitor:
            blocked_ips = self.monitor.get_suspicious_ips()
            self.blocked_ips_text.delete(1.0, tk.END)
            for ip in blocked_ips:
                self.blocked_ips_text.insert(tk.END, f"{ip}\n")
        
        # Schedule next update
        self.root.after(1000, self.update_blocked_ips)

def main():
    root = tk.Tk()
    app = DDoSSimulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 