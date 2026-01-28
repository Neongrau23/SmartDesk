import json
import os
import threading
import time
import psutil
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from ...shared.config import DATA_DIR
from ...shared.logging_config import get_logger
from ...shared.localization import get_text
from . import desktop_service
from . import settings_service

logger = get_logger(__name__)

RULES_FILE = os.path.join(DATA_DIR, "rules.json")


class AutoSwitchService:
    def __init__(self, check_interval: int = 2):
        self.check_interval = check_interval
        self._running = False
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._rules: Dict[str, str] = {}  # process_name -> desktop_name
        self._last_switch_time: Optional[datetime] = None
        self._cooldown_seconds = 60  # Minimum time between auto-switches
        self._lock = threading.RLock()
        self._rules_mtime = 0

        # Load rules on init
        self.load_rules()

    def load_rules(self):
        """Loads rules from the JSON file."""
        with self._lock:
            if not os.path.exists(RULES_FILE):
                self._rules = {}
                return

            try:
                mtime = os.path.getmtime(RULES_FILE)
                self._rules_mtime = mtime

                with open(RULES_FILE, "r", encoding="utf-8") as f:
                    self._rules = json.load(f)
            except Exception as e:
                logger.error(get_text("auto_switch.error.load_rules", e=e))
                self._rules = {}

    def _check_rules_file(self):
        """Reloads rules if file has changed on disk."""
        if not os.path.exists(RULES_FILE):
            return

        try:
            mtime = os.path.getmtime(RULES_FILE)
            if mtime > self._rules_mtime:
                logger.debug(get_text("auto_switch.debug.reload"))
                self.load_rules()
        except OSError:
            pass

    def save_rules(self):
        """Saves current rules to the JSON file."""
        with self._lock:
            try:
                # Ensure directory exists
                os.makedirs(os.path.dirname(RULES_FILE), exist_ok=True)
                with open(RULES_FILE, "w", encoding="utf-8") as f:
                    json.dump(self._rules, f, indent=4)

                # Update mtime to avoid reload loop
                if os.path.exists(RULES_FILE):
                    self._rules_mtime = os.path.getmtime(RULES_FILE)
            except Exception as e:
                logger.error(get_text("auto_switch.error.save_rules", e=e))

    def add_rule(self, process_name: str, desktop_name: str):
        """Adds or updates a rule."""
        # Normalize process name to lowercase for consistent matching
        process_name = process_name.lower()
        with self._lock:
            self._rules[process_name] = desktop_name
            self.save_rules()
        logger.info(get_text("auto_switch.info.added_rule", process=process_name, desktop=desktop_name))

    def delete_rule(self, process_name: str):
        """Deletes a rule."""
        process_name = process_name.lower()
        with self._lock:
            if process_name in self._rules:
                del self._rules[process_name]
                self.save_rules()
                logger.info(get_text("auto_switch.info.deleted_rule", process=process_name))
            else:
                logger.warning(get_text("auto_switch.warn.rule_not_found", process=process_name))

    def get_rules(self) -> Dict[str, str]:
        """Returns a copy of the current rules."""
        with self._lock:
            return self._rules.copy()

    def start(self):
        """Starts the monitoring thread."""
        if self._running:
            return

        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info(get_text("auto_switch.info.started"))

    def stop(self):
        """Stops the monitoring thread."""
        self._running = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)
        logger.info(get_text("auto_switch.info.stopped"))

    def _monitor_loop(self):
        """The main loop checking processes."""
        while not self._stop_event.is_set():
            try:
                self._check_rules_file()  # Check for external changes
                self._check_and_switch()
            except Exception as e:
                logger.error(get_text("auto_switch.error.loop", e=e))

            # Sleep with immediate wake-up on stop
            if self._stop_event.wait(self.check_interval):
                break

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

        # 3. Check processes against rules efficiently
        target_desktop_name = None
        matched_process = None

        with self._lock:
            # Snapshot rules as a list of (process_name, desktop_name)
            # Preserves priority order from JSON load (Python 3.7+ dicts preserve insertion order)
            rules_snapshot = list(self._rules.items())

        if not rules_snapshot:
            return

        # Map for O(1) lookup: process_name -> desktop_name
        rules_map = dict(rules_snapshot)
        # Map for O(1) priority lookup: process_name -> priority_index (0 is highest)
        rules_priority = {name: i for i, (name, _) in enumerate(rules_snapshot)}

        highest_priority_found_index = float("inf")

        try:
            # Optimization: Iterate psutil.process_iter only once and check against rules
            # instead of building a full set of ALL running processes.
            # Bolt optimization: Stop early if the highest priority rule is found.
            for proc in psutil.process_iter(["name"]):
                try:
                    pname = proc.info["name"]
                    if pname:
                        pname_lower = pname.lower()

                        if pname_lower in rules_map:
                            # We found a matching process
                            prio_index = rules_priority[pname_lower]

                            if prio_index < highest_priority_found_index:
                                highest_priority_found_index = prio_index
                                matched_process = pname_lower
                                target_desktop_name = rules_map[pname_lower]

                                # CRITICAL OPTIMIZATION:
                                # If we found the highest priority rule (index 0), we can STOP immediately.
                                # No need to check other processes.
                                if highest_priority_found_index == 0:
                                    break

                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception as e:
            logger.error(get_text("auto_switch.error.process_list", e=e))
            return

        if target_desktop_name:
            if active_desktop.name != target_desktop_name:
                logger.info(get_text("auto_switch.info.switching", desktop=target_desktop_name, process=matched_process))
                success = desktop_service.switch_to_desktop(target_desktop_name)
                if success:
                    self._last_switch_time = datetime.now()
            else:
                # We are already on the correct desktop.
                pass
