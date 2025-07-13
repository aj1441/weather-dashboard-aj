"""Automatic theme selection using location-based sunrise and sunset times."""

import logging
from datetime import datetime
from typing import Dict, Optional

from .location_service import LocationService, LocationInfo
from .theme_manager import ThemeManager
from .utils import UserSettingsManager

logger = logging.getLogger(__name__)


class AutoThemeManager:
    """Coordinate location lookups and theme recommendation."""

    def __init__(self, location_service: LocationService | None = None, settings: UserSettingsManager | None = None):
        self.location_service = location_service or LocationService()
        self.settings = settings or UserSettingsManager()
        self.current_location: Optional[LocationInfo] = None
        self.current_sun_times: Optional[Dict] = None

    def _resolve_location(self, latitude: float | None, longitude: float | None) -> Optional[LocationInfo]:
        if latitude is not None and longitude is not None:
            return LocationInfo(latitude=latitude, longitude=longitude, city="", country="", timezone_name="UTC")
        return self.location_service.get_user_location()

    def is_daytime(self, latitude: float | None = None, longitude: float | None = None) -> Optional[bool]:
        location = self._resolve_location(latitude, longitude)
        if not location:
            logger.warning("Could not determine location for day/night check")
            return None
        self.current_location = location
        result = self.location_service.is_daytime_now(location)
        if result is not None:
            sun = self.location_service.get_sunrise_sunset(location)
            if sun:
                self.current_sun_times = {
                    "sunrise": sun.sunrise,
                    "sunset": sun.sunset,
                }
        return result

    def get_recommended_theme(self, latitude: float | None = None, longitude: float | None = None) -> str:
        settings = self.settings.load_settings()
        auto_mode = settings.get("auto_theme_mode", True)
        light_theme = settings.get("light_theme", "aj_lightly")
        dark_theme = settings.get("dark_theme", "aj_darkly")
        theme_manager = ThemeManager()

        if not auto_mode:
            saved = self.settings.load_user_theme()
            return theme_manager.get_fallback_theme(saved)

        daytime = self.is_daytime(latitude, longitude)
        if daytime is None:
            saved = self.settings.load_user_theme()
            return theme_manager.get_fallback_theme(saved)

        chosen = light_theme if daytime else dark_theme
        return theme_manager.get_fallback_theme(chosen)

    def get_location_info(self) -> Optional[LocationInfo]:
        return self.current_location

    def get_sun_times(self) -> Optional[Dict]:
        return self.current_sun_times

def get_auto_theme(latitude: float | None = None, longitude: float | None = None) -> str:
    manager = AutoThemeManager()
    return manager.get_recommended_theme(latitude, longitude)

def is_daytime(latitude: float | None = None, longitude: float | None = None) -> bool:
    manager = AutoThemeManager()
    result = manager.is_daytime(latitude, longitude)
    return bool(result)
