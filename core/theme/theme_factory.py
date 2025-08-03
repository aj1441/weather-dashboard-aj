"""
Theme system factory for easy setup and dependency injection.

This module provides factories to create properly configured theme managers
with all dependencies wired up correctly.
"""

from typing import Optional, Union
import logging

from .theme_system import ThemeConfig, ThemeManager
from .theme_implementations import (
    JsonThemeSettings,
    LocationBasedAutoThemeService,
    SimpleTimeBasedAutoThemeService,
    TtkBootstrapThemeApplicator,
    MockThemeSettings,
    MockAutoThemeService,
    MockThemeApplicator
)

logger = logging.getLogger(__name__)


class ThemeManagerFactory:
    """Factory for creating configured theme managers."""
    
    @classmethod
    def create_default(cls, 
                      app_instance=None,
                      config: Optional[ThemeConfig] = None) -> ThemeManager:
        """
        Create a theme manager with default production implementations.
        
        Args:
            app_instance: Optional ttkbootstrap app instance for theme application
            config: Optional custom configuration (uses defaults if None)
            
        Returns:
            Fully configured ThemeManager instance
        """
        if config is None:
            config = ThemeConfig()
        
        # Create implementations
        settings = JsonThemeSettings(config)
        auto_service = LocationBasedAutoThemeService()
        applicator = TtkBootstrapThemeApplicator(app_instance)
        
        # Create and return manager
        manager = ThemeManager(
            config=config,
            settings=settings,
            auto_service=auto_service,
            applicator=applicator
        )
        
        logger.info("Created default theme manager with auto-theme enabled")
        return manager
    
    @classmethod
    def create_simple_time_based(cls,
                                app_instance=None,
                                config: Optional[ThemeConfig] = None,
                                day_start_hour: int = 6,
                                night_start_hour: int = 18) -> ThemeManager:
        """
        Create a theme manager with simple time-based auto theme service.
        
        This is useful when location services aren't available or desired.
        
        Args:
            app_instance: Optional ttkbootstrap app instance
            config: Optional custom configuration
            day_start_hour: Hour when day theme should start (default: 6 AM)
            night_start_hour: Hour when night theme should start (default: 6 PM)
            
        Returns:
            ThemeManager with simple time-based auto switching
        """
        if config is None:
            config = ThemeConfig()
        
        # Create implementations
        settings = JsonThemeSettings(config)
        auto_service = SimpleTimeBasedAutoThemeService(day_start_hour, night_start_hour)
        applicator = TtkBootstrapThemeApplicator(app_instance)
        
        # Create and return manager
        manager = ThemeManager(
            config=config,
            settings=settings,
            auto_service=auto_service,
            applicator=applicator
        )
        
        logger.info(f"Created time-based theme manager (day: {day_start_hour}, night: {night_start_hour})")
        return manager
    
    @classmethod
    def create_for_testing(cls,
                          config: Optional[ThemeConfig] = None,
                          is_daytime: Optional[bool] = True) -> ThemeManager:
        """
        Create a theme manager with mock implementations for testing.
        
        Args:
            config: Optional custom configuration
            is_daytime: Initial daytime status for auto theme testing
            
        Returns:
            ThemeManager with mock implementations
        """
        if config is None:
            config = ThemeConfig()
        
        # Create mock implementations
        settings = MockThemeSettings(config)
        auto_service = MockAutoThemeService(is_daytime)
        applicator = MockThemeApplicator()
        
        # Create and return manager
        manager = ThemeManager(
            config=config,
            settings=settings,
            auto_service=auto_service,
            applicator=applicator
        )
        
        logger.info(f"Created test theme manager (daytime: {is_daytime})")
        return manager
    
    @classmethod
    def create_with_custom_config(cls,
                                 app_instance=None,
                                 default_light_theme: str = "aj_lightly",
                                 default_dark_theme: str = "aj_darkly",
                                 auto_enabled_by_default: bool = True,
                                 fallback_theme: str = "flatly",
                                 settings_file: str = "data/user_settings.json") -> ThemeManager:
        """
        Create a theme manager with custom configuration.
        
        Args:
            app_instance: Optional ttkbootstrap app instance
            default_light_theme: Default light theme name
            default_dark_theme: Default dark theme name
            auto_enabled_by_default: Whether auto mode is enabled by default
            fallback_theme: Fallback theme if others fail
            settings_file: Path to settings file
            
        Returns:
            ThemeManager with custom configuration
        """
        config = ThemeConfig(
            default_light_theme=default_light_theme,
            default_dark_theme=default_dark_theme,
            auto_enabled_by_default=auto_enabled_by_default,
            fallback_theme=fallback_theme,
            settings_file=settings_file
        )
        
        return cls.create_default(app_instance, config)


class ThemeSystemBuilder:
    """Builder pattern for more complex theme system configuration."""
    
    def __init__(self):
        self._config = None
        self._settings = None
        self._auto_service = None
        self._applicator = None
        self._app_instance = None
    
    def with_config(self, config: ThemeConfig) -> 'ThemeSystemBuilder':
        """Set custom configuration."""
        self._config = config
        return self
    
    def with_app_instance(self, app_instance) -> 'ThemeSystemBuilder':
        """Set ttkbootstrap app instance."""
        self._app_instance = app_instance
        return self
    
    def with_json_settings(self, settings_file: Optional[str] = None) -> 'ThemeSystemBuilder':
        """Use JSON file for settings storage."""
        config = self._config or ThemeConfig()
        if settings_file:
            config = ThemeConfig(
                default_light_theme=config.default_light_theme,
                default_dark_theme=config.default_dark_theme,
                auto_enabled_by_default=config.auto_enabled_by_default,
                fallback_theme=config.fallback_theme,
                settings_file=settings_file
            )
            self._config = config
        
        self._settings = JsonThemeSettings(config)
        return self
    
    def with_location_based_auto_theme(self) -> 'ThemeSystemBuilder':
        """Use location-based auto theme service."""
        self._auto_service = LocationBasedAutoThemeService()
        return self
    
    def with_time_based_auto_theme(self, 
                                  day_start: int = 6, 
                                  night_start: int = 18) -> 'ThemeSystemBuilder':
        """Use simple time-based auto theme service."""
        self._auto_service = SimpleTimeBasedAutoThemeService(day_start, night_start)
        return self
    
    def with_ttkbootstrap_applicator(self) -> 'ThemeSystemBuilder':
        """Use ttkbootstrap theme applicator."""
        self._applicator = TtkBootstrapThemeApplicator(self._app_instance)
        return self
    
    def with_mock_components(self, is_daytime: Optional[bool] = True) -> 'ThemeSystemBuilder':
        """Use mock components for testing."""
        config = self._config or ThemeConfig()
        self._settings = MockThemeSettings(config)
        self._auto_service = MockAutoThemeService(is_daytime)
        self._applicator = MockThemeApplicator()
        return self
    
    def build(self) -> ThemeManager:
        """Build the theme manager with configured components."""
        # Use defaults if not set
        config = self._config or ThemeConfig()
        
        if self._settings is None:
            self._settings = JsonThemeSettings(config)
        
        if self._auto_service is None:
            self._auto_service = LocationBasedAutoThemeService()
        
        if self._applicator is None:
            self._applicator = TtkBootstrapThemeApplicator(self._app_instance)
        
        return ThemeManager(
            config=config,
            settings=self._settings,
            auto_service=self._auto_service,
            applicator=self._applicator
        )


# ============================================================================
# Convenience Functions
# ============================================================================

def create_theme_manager(app_instance=None, **config_kwargs) -> ThemeManager:
    """
    Convenience function to create a theme manager with sensible defaults.
    
    Args:
        app_instance: Optional ttkbootstrap app instance
        **config_kwargs: Configuration options to override defaults
        
    Returns:
        Configured ThemeManager instance
    """
    if config_kwargs:
        return ThemeManagerFactory.create_with_custom_config(app_instance, **config_kwargs)
    else:
        return ThemeManagerFactory.create_default(app_instance)


def create_simple_theme_manager(app_instance=None, 
                               day_hour: int = 6, 
                               night_hour: int = 18) -> ThemeManager:
    """
    Convenience function to create a theme manager with simple time-based switching.
    
    Args:
        app_instance: Optional ttkbootstrap app instance
        day_hour: Hour when day theme starts (default: 6 AM)
        night_hour: Hour when night theme starts (default: 6 PM)
        
    Returns:
        ThemeManager with time-based auto switching
    """
    return ThemeManagerFactory.create_simple_time_based(
        app_instance=app_instance,
        day_start_hour=day_hour,
        night_start_hour=night_hour
    )


def create_test_theme_manager(is_daytime: Optional[bool] = True) -> ThemeManager:
    """
    Convenience function to create a theme manager for testing.
    
    Args:
        is_daytime: Initial daytime status
        
    Returns:
        ThemeManager with mock implementations
    """
    return ThemeManagerFactory.create_for_testing(is_daytime=is_daytime)