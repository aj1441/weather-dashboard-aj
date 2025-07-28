"""About component for displaying application information"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
import logging
from PIL import Image, ImageTk
import os

logger = logging.getLogger(__name__)

class AboutComponent:
    """Component for displaying application information and credits"""
    
    def __init__(self, parent):
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        
        # UI components
        self.main_frame = None
        self.logo_label = None
        
    def setup_component(self):
        """Create and setup the about component"""
        # Main container frame
        self.main_frame = tb.Frame(self.parent)
        
        # Create main content frame directly (no scrollable frame for now)
        content_frame = tb.Frame(self.main_frame)
        content_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Configure grid for two-column layout
        content_frame.columnconfigure(0, weight=2)  # Left column (text) - 2 parts
        content_frame.columnconfigure(1, weight=3)  # Right column (logo) - 3 parts (more space)
        content_frame.rowconfigure(2, weight=1)     # Main content row
        
        # Title and version (span both columns)
        title_label = tb.Label(
            content_frame,
            text="Advanced Weather Dashboard",
            font=("Helvetica Neue", 24, "bold"),
            bootstyle="primary"
        )
        title_label.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        version_label = tb.Label(
            content_frame,
            text="Version 2.0.0",
            font=("Helvetica Neue", 12),
            bootstyle="secondary"
        )
        version_label.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        # Left content frame (text)
        left_content_frame = tb.Frame(content_frame)
        left_content_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 20))
        # left_content_frame.configure(bg="#2b2b2b")  # Dark grey background
        
        # Debug: Add border to left content frame
        # left_content_frame.configure(relief="solid", borderwidth=2, bg="orange")  # Debug: orange border
        
        # Application description
        description_label = tb.Label(
            left_content_frame,
            text="A comprehensive weather dashboard application built with modern Python technologies. "
                 "Features a component-based architecture for maintainability and extensibility.",
            font=("Helvetica Neue", 11),
            wraplength=400,
            justify=LEFT
        )
        description_label.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Features section
        features_label = tb.Label(
            left_content_frame,
            text="🌟 Key Features:",
            font=("Helvetica Neue", 14, "bold"),
            bootstyle="primary"
        )
        features_label.grid(row=1, column=0, sticky="w", pady=(0, 10))
        
        features_text = [
            "🌤️ Current Weather - Real-time weather data from OpenWeather API with detailed conditions",
            "📅 7-Day Forecast - Extended weather forecasts with intelligent data extension",
            "💾 Save Cities - Persistent storage of favorite locations with database integration",
            "📊 Weather History - Complete weather history tracking with searchable records",
            "🎨 Custom Themes - Multiple themes including custom aj_darkly and aj_lightly designs",
            "🌙 Auto Day/Night - Automatic theme switching based on time and location",
            "🗄️ Database Storage - SQLite database for reliable data persistence",
            "🔧 Component Architecture - Modular design with reusable UI components",
            "🎯 Weather Trivia - Interactive weather knowledge game with sound effects",
            "📈 Historical Analysis - Advanced charting and data visualization",
            "🔄 API Fallback - Robust fallback system for reliable data access",
            "⚡ Performance Optimized - Caching, connection pooling, and monitoring"
        ]
        
        for i, feature in enumerate(features_text):
            feature_label = tb.Label(
                left_content_frame,
                text=feature,
                font=("Helvetica Neue", 10),
                wraplength=380,
                justify=LEFT
            )
            feature_label.grid(row=2+i, column=0, sticky="w", pady=(2, 0))
        
        # Technical details section
        tech_label = tb.Label(
            left_content_frame,
            text="🔧 Technical Architecture:",
            font=("Helvetica Neue", 14, "bold"),
            bootstyle="primary"
        )
        tech_label.grid(row=len(features_text)+2, column=0, sticky="w", pady=(20, 10))
        
        tech_text = [
            "• Python 3.13 with modern async/await patterns",
            "• Tkinter/TtkBootstrap for responsive GUI",
            "• SQLite database with optimized queries",
            "• RESTful API integration with fallback systems",
            "• Component-based architecture for scalability",
            "• Comprehensive logging and error handling",
            "• Performance monitoring and optimization",
            "• Modular design with clear separation of concerns"
        ]
        
        for i, tech in enumerate(tech_text):
            tech_label = tb.Label(
                left_content_frame,
                text=tech,
                font=("Helvetica Neue", 10),
                wraplength=380,
                justify=LEFT
            )
            tech_label.grid(row=len(features_text)+3+i, column=0, sticky="w", pady=(2, 0))
        
        # Right content frame (logo)
        right_content_frame = tb.Frame(content_frame)
        right_content_frame.grid(row=2, column=1, sticky="nsew", padx=(20, 0))
        right_content_frame.rowconfigure(0, weight=1)
        right_content_frame.columnconfigure(0, weight=1)
        # right_content_frame.configure(bg="#2b2b2b")  # Dark grey background
        
        # Debug: Add border to right content frame
        # right_content_frame.configure(relief="solid", borderwidth=2, bg="yellow")  # Debug: yellow border
        
        # Ensure the right frame expands to fill available space
        content_frame.rowconfigure(2, weight=1)
        
        # Add logo
        self._add_logo(right_content_frame)
        
        # Status section (span both columns at bottom)
        status_frame = tb.Frame(content_frame)
        status_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(30, 0))
        
        status_label = tb.Label(
            status_frame,
            text="🟢 Status: Application running successfully",
            font=("Helvetica Neue", 10),
            bootstyle="success"
        )
        status_label.pack(side=LEFT)
        
        # Credits section
        credits_label = tb.Label(
            status_frame,
            text="Developed with ❤️ using Python and modern web technologies",
            font=("Helvetica Neue", 10),
            bootstyle="secondary"
        )
        credits_label.pack(side=RIGHT)
        
        return self.main_frame
    
    def _add_logo(self, parent_frame):
        """Add the application logo to the right content frame"""
        try:
            # Try to load the logo image
            logo_paths = [
                "assets/images/art_logo.png",
                "assets/images/enhanced_logo_clean.png"
            ]
            
            logo_image = None
            for logo_path in logo_paths:
                if os.path.exists(logo_path):
                    try:
                        # Load and process the image with size limit
                        image = Image.open(logo_path)
                        
                        # Check image size and resize if too large to prevent memory issues
                        max_size = 800  # Limit maximum dimension
                        if image.width > max_size or image.height > max_size:
                            # Calculate new size maintaining aspect ratio
                            ratio = min(max_size / image.width, max_size / image.height)
                            new_width = int(image.width * ratio)
                            new_height = int(image.height * ratio)
                            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                            self.logger.info(f"Resized large logo from {logo_path} to {new_width}x{new_height}")
                        
                        # Convert to RGBA if not already
                        if image.mode != 'RGBA':
                            image = image.convert('RGBA')
                        
                        # Create a transparent background
                        transparent_bg = Image.new('RGBA', image.size, (0, 0, 0, 0))
                        
                        # Composite the image onto transparent background
                        final_image = Image.alpha_composite(transparent_bg, image)
                        
                        # Resize to 400x400 while maintaining aspect ratio
                        final_image.thumbnail((400, 400), Image.Resampling.LANCZOS)
                        
                        # Convert to PhotoImage
                        logo_image = ImageTk.PhotoImage(final_image)
                        self.logger.info(f"About tab logo added successfully from {logo_path}")
                        break
                    except Exception as e:
                        self.logger.warning(f"Failed to load logo from {logo_path}: {e}")
                        continue
            
            if logo_image:
                self.logo_label = tb.Label(
                    parent_frame,
                    image=logo_image
                )
                self.logo_label.image = logo_image  # Keep a reference
                self.logo_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
                self.logger.info("About tab logo added successfully")
            else:
                # Fallback text if no logo found
                fallback_label = tb.Label(
                    parent_frame,
                    text="🌤️\nWeather\nDashboard",
                    font=("Helvetica Neue", 24, "bold"),
                    justify=CENTER,
                    bootstyle="primary"
                )
                fallback_label.grid(row=0, column=0, sticky="nsew")
                self.logger.warning("Logo not found, using fallback text")
                
        except Exception as e:
            self.logger.error(f"Error loading logo: {e}")
            # Fallback text on error
            fallback_label = tb.Label(
                parent_frame,
                text="🌤️\nWeather\nDashboard",
                font=("Helvetica Neue", 24, "bold"),
                justify=CENTER,
                bootstyle="primary"
            )
            fallback_label.grid(row=0, column=0, sticky="nsew")
    
    def refresh(self):
        """Refresh the component (called when theme changes)"""
        # The logo and text will automatically adapt to theme changes
        pass 