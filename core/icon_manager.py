"""Icon and image management system for the weather dashboard"""

import os
import tkinter as tk
from typing import Dict, Optional, Tuple
from PIL import Image, ImageTk
import ttkbootstrap as tb

class IconManager:
    """Centralized icon and image management system"""
    
    def __init__(self, assets_path: str = "assets"):
        self.assets_path = assets_path
        self.icons_path = os.path.join(assets_path, "icons")
        self.images_path = os.path.join(assets_path, "images")
        
        # Cache for loaded images to avoid reloading
        self._image_cache: Dict[str, ImageTk.PhotoImage] = {}
        self._icon_cache: Dict[str, ImageTk.PhotoImage] = {}
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Icon mappings - you can extend this
        self.icon_map = {
            # Weather icons
            "sunny": "☀️",
            "cloudy": "☁️", 
            "rainy": "🌧️",
            "snowy": "❄️",
            "partly_cloudy": "🌤️",
            "thunderstorm": "⛈️",
            "windy": "🌬️",
            "temperature": "🌡️",
            
            # UI icons
            "save": "💾",
            "star": "⭐",
            "heart": "❤️",
            "location": "📍",
            "search": "🔍",
            "refresh": "🔄",
            "settings": "⚙️",
            "chart": "📊",
            "history": "📋",
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "success": "✅",
            
            # Navigation icons
            "home": "🏠",
            "back": "⬅️",
            "forward": "➡️",
            "up": "⬆️",
            "down": "⬇️",
            
            # Theme icons
            "light": "☀️",
            "dark": "🌙",
            
            # Additional weather related
            "humidity": "💧",
            "pressure": "🌡️",
            "wind": "🌬️",
            "visibility": "👁️"
        }
    
    def _ensure_directories(self) -> None:
        """Create asset directories if they don't exist"""
        os.makedirs(self.icons_path, exist_ok=True)
        os.makedirs(self.images_path, exist_ok=True)
    
    def get_emoji_icon(self, icon_name: str) -> str:
        """
        Get emoji icon by name
        
        Args:
            icon_name: Name of the icon
            
        Returns:
            Emoji character or default if not found
        """
        return self.icon_map.get(icon_name, "❓")
    
    def load_image(self, image_name: str, size: Optional[Tuple[int, int]] = None) -> Optional[ImageTk.PhotoImage]:
        """
        Load an image file and optionally resize it
        
        Args:
            image_name: Name of the image file (with or without extension)
            size: Optional tuple of (width, height) for resizing
            
        Returns:
            PhotoImage object or None if loading fails
        """
        cache_key = f"{image_name}_{size}" if size else image_name
        
        # Check cache first
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]
        
        # Try different extensions
        extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        image_path = None
        
        for ext in extensions:
            potential_path = os.path.join(self.images_path, f"{image_name}{ext}")
            if os.path.exists(potential_path):
                image_path = potential_path
                break
        
        if not image_path:
            print(f"Image not found: {image_name}")
            return None
        
        try:
            # Load and optionally resize image
            img = Image.open(image_path)
            if size:
                img = img.resize(size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo_img = ImageTk.PhotoImage(img)
            
            # Cache the result
            self._image_cache[cache_key] = photo_img
            
            return photo_img
        
        except Exception as e:
            print(f"Error loading image {image_name}: {e}")
            return None
    
    def load_icon(self, icon_name: str, size: Tuple[int, int] = (24, 24)) -> Optional[ImageTk.PhotoImage]:
        """
        Load an icon file with specific size
        
        Args:
            icon_name: Name of the icon file
            size: Tuple of (width, height) for the icon size
            
        Returns:
            PhotoImage object or None if loading fails
        """
        cache_key = f"icon_{icon_name}_{size}"
        
        # Check cache first
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]
        
        # Try different extensions
        extensions = ['.png', '.svg', '.ico', '.jpg', '.jpeg']
        icon_path = None
        
        for ext in extensions:
            potential_path = os.path.join(self.icons_path, f"{icon_name}{ext}")
            if os.path.exists(potential_path):
                icon_path = potential_path
                break
        
        if not icon_path:
            print(f"Icon not found: {icon_name}")
            return None
        
        try:
            # Load and resize icon
            img = Image.open(icon_path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo_img = ImageTk.PhotoImage(img)
            
            # Cache the result
            self._icon_cache[cache_key] = photo_img
            
            return photo_img
        
        except Exception as e:
            print(f"Error loading icon {icon_name}: {e}")
            return None
    
    def create_button_with_icon(self, parent, text: str = "", icon_name: str = "", 
                               command=None, bootstyle: str = "primary", 
                               icon_size: Tuple[int, int] = (16, 16)) -> tb.Button:
        """
        Create a button with an icon
        
        Args:
            parent: Parent widget
            text: Button text
            icon_name: Name of the icon (will try file first, then emoji)
            command: Button command
            bootstyle: Button style
            icon_size: Size of the icon
            
        Returns:
            Button widget
        """
        # Try to load file icon first
        icon_image = self.load_icon(icon_name, icon_size)
        
        if icon_image:
            # Use file icon
            if text:
                return tb.Button(parent, text=text, image=icon_image, compound="left", 
                               command=command, bootstyle=bootstyle)
            else:
                return tb.Button(parent, image=icon_image, command=command, bootstyle=bootstyle)
        else:
            # Fall back to emoji icon
            emoji = self.get_emoji_icon(icon_name)
            button_text = f"{emoji} {text}" if text else emoji
            return tb.Button(parent, text=button_text, command=command, bootstyle=bootstyle)
    
    def get_weather_icon(self, description: str, size: Tuple[int, int] = (48, 48)) -> str:
        """
        Get weather icon based on description (enhanced version)
        
        Args:
            description: Weather description
            size: Icon size (for future file icon support)
            
        Returns:
            Icon (emoji for now, could be file path later)
        """
        d = description.lower()
        
        # Map weather descriptions to icon names
        if "clear" in d or "sky is clear" in d:
            return self.get_emoji_icon("sunny")
        elif "few clouds" in d or "partly" in d:
            return self.get_emoji_icon("partly_cloudy")
        elif "scattered clouds" in d or "broken clouds" in d or "cloud" in d or "overcast" in d:
            return self.get_emoji_icon("cloudy")
        elif "wind" in d:
            return self.get_emoji_icon("windy")
        elif "rain" in d or "drizzle" in d or "shower" in d:
            return self.get_emoji_icon("rainy")
        elif "thunder" in d or "storm" in d:
            return self.get_emoji_icon("thunderstorm")
        elif "snow" in d or "sleet" in d:
            return self.get_emoji_icon("snowy")
        elif "mist" in d or "fog" in d:
            return "🌫️"
        else:
            return self.get_emoji_icon("partly_cloudy")
    
    def clear_cache(self) -> None:
        """Clear the image cache to free memory"""
        self._image_cache.clear()
        self._icon_cache.clear()
    
    def add_custom_icon(self, name: str, emoji: str) -> None:
        """
        Add a custom emoji icon to the map
        
        Args:
            name: Icon name
            emoji: Emoji character
        """
        self.icon_map[name] = emoji

# Global icon manager instance
_icon_manager = None

def get_icon_manager() -> IconManager:
    """Get the global icon manager instance"""
    global _icon_manager
    if _icon_manager is None:
        _icon_manager = IconManager()
    return _icon_manager

# Convenience functions
def get_icon(icon_name: str) -> str:
    """Get emoji icon by name"""
    return get_icon_manager().get_emoji_icon(icon_name)

def get_weather_icon(description: str) -> str:
    """Get weather icon by description"""
    return get_icon_manager().get_weather_icon(description)

def create_icon_button(parent, text: str = "", icon_name: str = "", 
                      command=None, bootstyle: str = "primary") -> tb.Button:
    """Create a button with an icon"""
    return get_icon_manager().create_button_with_icon(
        parent, text, icon_name, command, bootstyle
    )
