import urllib.request
import json
import logging
from typing import Optional, Tuple, Dict, Any
from smartdesk import __version__
from smartdesk.shared.logging_config import get_logger
from smartdesk.core.services import settings_service # Import settings_service

logger = get_logger(__name__)

class UpdateService:
    """Service to check for updates on GitHub."""
    
    GITHUB_API_URL = "https://api.github.com/repos/Neongrau23/SmartDesk/releases/latest"
    
    def __init__(self):
        self.latest_release_info: Optional[Dict[str, Any]] = None

    def check_for_updates(self) -> Tuple[bool, Optional[str]]:
        """
        Checks if a newer version is available on GitHub.
        
        Returns:
            Tuple[bool, Optional[str]]: (is_newer_version_available, latest_version_string)
        """
        try:
            # Use a User-Agent to avoid being blocked by GitHub API
            headers = {'User-Agent': 'SmartDesk-Update-Checker'}

            github_pat = settings_service.get_setting("github_pat")
            if github_pat:
                headers['Authorization'] = f'token {github_pat}'

            req = urllib.request.Request(self.GITHUB_API_URL, headers=headers)

            with urllib.request.urlopen(req, timeout=10) as response:
                logger.debug(f"GitHub API response status: {response.status}")
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    self.latest_release_info = data
                    logger.debug(f"GitHub API response data: {data}")

                    remote_version_raw = data.get("tag_name", "0.0.0")
                    if not remote_version_raw:
                        logger.warning("tag_name not found in GitHub API response.")
                        return False, None
                    
                    remote_version = remote_version_raw.lstrip('v')

                    if self._is_version_newer(__version__, remote_version):
                        logger.info(f"New version available: {remote_version} (current: {__version__})")
                        return True, remote_version

                    logger.info(f"SmartDesk is up to date (current: {__version__})")
                    return False, remote_version
                else:
                    logger.error(f"GitHub API returned status code: {response.status}")
        except urllib.error.HTTPError as http_e:
            if http_e.code == 403:
                logger.error(f"GitHub API rate limit exceeded: {http_e}", exc_info=True)
                return False, "RATE_LIMIT_EXCEEDED"
            else:
                logger.error(f"Failed to check for updates (HTTP Error {http_e.code}): {http_e}", exc_info=True)
                return False, None
        except Exception as e:
            logger.error(f"Failed to check for updates: {e}", exc_info=True)

        return False, None

    def get_download_url(self) -> Optional[str]:
        """Returns the download URL for the Windows executable asset if available."""
        if not self.latest_release_info:
            return None

        assets = self.latest_release_info.get("assets", [])
        for asset in assets:
            name = asset.get("name", "").lower()
            # Look for common installer patterns
            if name.endswith(".exe") or "setup" in name or "installer" in name:
                return asset.get("browser_download_url")

        # Fallback to the release page if no direct exe asset is found
        return self.latest_release_info.get("html_url")

    def _is_version_newer(self, current: str, remote: str) -> bool:
        """Simple semantic version comparison."""
        try:
            c_parts = [int(p) for p in current.split('.')]
            r_parts = [int(p) for p in remote.split('.')]

            # Pad with zeros if necessary (e.g. 1.0 vs 1.0.1)
            length = max(len(c_parts), len(r_parts))
            c_parts.extend([0] * (length - len(c_parts)))
            r_parts.extend([0] * (length - len(r_parts)))

            return r_parts > c_parts
        except Exception:
            # Fallback to simple string comparison if format is unexpected
            return remote > current
