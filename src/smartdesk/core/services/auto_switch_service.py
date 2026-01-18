import json
import os
import threading
import time
import psutil
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from ...shared.config import DATA_DIR
from ...shared.logging_config import get_logger
from . import desktop_service
from . import settings_service

logger = get_logger(__name__)

RULES_FILE = os.path.join(DATA_DIR, "rules.json")

class AutoSwitchService:
    def __init__(self, check_interval: int = 2):
        self.check_interval = check_interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._rules: Dict[str, str] = {}  # process_name -> desktop_name
        self._last_switch_time: Optional[datetime] = None
        self._cooldown_seconds = 60  # Minimum time between auto-switches
        self._lock = threading.RLock()

        # Load rules on init
        self.load_rules()

    def load_rules(self):
        """Loads rules from the JSON file."""
        with self._lock:
            if not os.path.exists(RULES_FILE):
                self._rules = {}
                return

            try:
                with open(RULES_FILE, 'r', encoding='utf-8') as f:
                    self._rules = json.load(f)
            except Exception as e:
                logger.error(f"Error loading rules: {e}")
                self._rules = {}

    def save_rules(self):
        """Saves current rules to the JSON file."""
        with self._lock:
            try:
                # Ensure directory exists
                os.makedirs(os.path.dirname(RULES_FILE), exist_ok=True)
                with open(RULES_FILE, 'w', encoding='utf-8') as f:
                    json.dump(self._rules, f, indent=4)
            except Exception as e:
                logger.error(f"Error saving rules: {e}")

    def add_rule(self, process_name: str, desktop_name: str):
        """Adds or updates a rule."""
        # Normalize process name to lowercase for consistent matching
        process_name = process_name.lower()
        with self._lock:
            self._rules[process_name] = desktop_name
            self.save_rules()
        logger.info(f"Added rule: {process_name} -> {desktop_name}")

    def delete_rule(self, process_name: str):
        """Deletes a rule."""
        process_name = process_name.lower()
        with self._lock:
            if process_name in self._rules:
                del self._rules[process_name]
                self.save_rules()
                logger.info(f"Deleted rule for: {process_name}")
            else:
                logger.warning(f"Rule not found for: {process_name}")

    def get_rules(self) -> Dict[str, str]:
        """Returns a copy of the current rules."""
        with self._lock:
            return self._rules.copy()

    def start(self):
        """Starts the monitoring thread."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info("AutoSwitchService started.")

    def stop(self):
        """Stops the monitoring thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        logger.info("AutoSwitchService stopped.")

    def _monitor_loop(self):
        """The main loop checking processes."""
        while self._running:
            try:
                self._check_and_switch()
            except Exception as e:
                logger.error(f"Error in AutoSwitchService loop: {e}")

            # Sleep in small chunks to allow faster stopping
            for _ in range(self.check_interval * 2):
                if not self._running:
                    break
                time.sleep(0.5)

    def _check_and_switch(self):
        """Checks running processes and switches desktop if needed."""
        # 0. Check global setting
        if not settings_service.get_setting("auto_switch_enabled", False):
            return

        # 1. Check cooldown
        if self._last_switch_time:
            elapsed = (datetime.now() - self._last_switch_time).total_seconds()
            if elapsed < self._cooldown_seconds:
                return

        # 2. Get active desktop
        desktops = desktop_service.get_all_desktops()
        active_desktop = next((d for d in desktops if d.is_active), None)

        if not active_desktop:
            return

        # 3. Get running processes (only names)
        # Iterate over all running processes
        running_process_names = set()
        try:
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name']:
                        running_process_names.add(proc.info['name'].lower())
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception as e:
            logger.error(f"Error accessing process list: {e}")
            return

        # 4. Check against rules
        # We need to find if any priority process is running.
        # If multiple rules match, which one takes precedence?
        # For now, let's take the first one found in the rules list (arbitrary order).
        # Or maybe we iterate rules and check if process is running.

        target_desktop_name = None
        matched_process = None

        with self._lock:
            # Check if any ruled process is running
            for proc_name, desktop_name in self._rules.items():
                if proc_name in running_process_names:
                    # Found a running process that has a rule

                    # Optimization: If we are already on the target desktop, we might want to stay there
                    # But maybe there's another process that wants a different desktop?
                    # Let's simple pick the first one.
                    target_desktop_name = desktop_name
                    matched_process = proc_name
                    break

        if target_desktop_name:
            if active_desktop.name != target_desktop_name:
                logger.info(f"Auto-switching to '{target_desktop_name}' detected process '{matched_process}'")
                success = desktop_service.switch_to_desktop(target_desktop_name)
                if success:
                    self._last_switch_time = datetime.now()
            else:
                # We are already on the correct desktop.
                pass
