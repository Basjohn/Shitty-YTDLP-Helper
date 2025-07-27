import sys
import subprocess
import platform
import os
import webbrowser
import shutil
import threading
import requests
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QDialog,
    QCheckBox, QLineEdit, QPushButton, QMenu, QMessageBox, QHBoxLayout,
    QSizePolicy
)
from PySide6.QtCore import Qt, QPoint, QPointF, QTimer, QSize, Signal, QProcess, QRect
from PySide6.QtGui import QCursor, QMouseEvent, QColor, QPainter, QIcon, QPixmap, QPainterPath

class ClickableLabel(QLabel):
    doubleClicked = Signal()
    
    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)


class ShittyYTDLPHelper(QWidget):
    VERSION = "1.1Two"
    
    # Signal to update the button from any thread
    update_button_signal = Signal()
    
    def __init__(self):
        super().__init__()
        # Initialize all instance variables first
        self.latest_version = None
        self.update_available = False
        self.download_url = None
        self.update_button = None  # Will be set in init_ui
        self.drag_pos = None
        self.snap_threshold = 20
        
        # Set project directory and ensure downloads directory exists
        # Handle PyInstaller bundled executable
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # Running as PyInstaller bundle - use executable directory
            self.project_dir = os.path.dirname(sys.executable)
        else:
            # Running as script - use script directory
            self.project_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.downloads_dir = os.path.join(self.project_dir, 'downloads')
        os.makedirs(self.downloads_dir, exist_ok=True)
        
        # Set up window properties
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set application name for taskbar and process name
        if platform.system() == 'Windows':
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('SYH.App')
        
        # Set window title
        self.setWindowTitle(f"Shitty YTDLP Helper v{self.VERSION}")
        
        # Set application and window icons for taskbar
        icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rc')
        icon_ext = '.ico' if platform.system() == 'Windows' else '.png'
        icon_path = os.path.join(icon_dir, f'SYHSB{icon_ext}')
        
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            QApplication.setWindowIcon(app_icon)
            self.setWindowIcon(app_icon)

        # Initialize UI and start background tasks
        self.init_ui()
        QTimer.singleShot(100, self.center_on_screen)
        # Start update check after UI is fully initialized (2 second delay)
        QTimer.singleShot(2000, self.start_update_check)
    
    def open_downloads_folder(self):
        """Open the downloads folder in the system file explorer."""
        try:
            # Ensure the directory exists before trying to open it
            os.makedirs(self.downloads_dir, exist_ok=True)
            
            if platform.system() == "Windows":
                os.startfile(os.path.normpath(self.downloads_dir))
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", os.path.normpath(self.downloads_dir)])
            else:
                subprocess.Popen(["xdg-open", os.path.normpath(self.downloads_dir)])
        except Exception as e:
            self.show_custom_message("Error", f"Could not open downloads folder:\n{str(e)}\nPath: {os.path.abspath(self.downloads_dir)}")

    def open_project_folder(self):
        """Open the project folder in the system file explorer."""
        try:
            path = Path(self.project_dir).resolve()
            if platform.system() == 'Windows':
                os.startfile(path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', str(path)])
            else:  # Linux and other Unix-like
                subprocess.run(['xdg-open', str(path)])
        except Exception as e:
            QMessageBox.warning(
                self,
                'Error',
                f'Could not open project folder: {str(e)}',
                QMessageBox.Ok
            )

    def center_on_screen(self):
        """Center the window on the screen."""
        frame_geometry = self.frameGeometry()
        screen = QApplication.primaryScreen().availableGeometry()
        frame_geometry.moveCenter(screen.center())
        self.move(frame_geometry.topLeft())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw the white 3px border first
        painter.setPen(QColor("white"))
        painter.setBrush(Qt.NoBrush)
        for i in range(3):
            painter.drawRoundedRect(self.rect().adjusted(i, i, -i, -i), 20-i, 20-i)
        
        # Draw background with 80% opacity, contained within border
        bg_color = QColor(42, 42, 42, 204)  # 80% opacity
        painter.setBrush(bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect().adjusted(3, 3, -3, -3), 17, 17)

    def init_ui(self):
        base_color = QColor("#2a2a2a")
        darker_color = QColor("#1c1c1c")
        text_color = QColor("white")

        self.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
                color: {text_color.name()};
                font-family: Arial;
            }}
            QMenu {{
                background-color: {base_color.name()};
                color: {text_color.name()};
                border: 1px solid white;
                border-radius: 8px;
                padding: 5px;
            }}
            QMenu::item {{
                padding: 8px 20px;
                background-color: transparent;
            }}
            QMenu::item:selected {{
                background-color: {darker_color.name()};
            }}
            QLabel#heading {{
                background-color: {darker_color.name()};
                font-size: 28px;
                font-weight: bold;
                border: 1px solid white;
                border-radius: 15px;
                padding: 10px;
                qproperty-alignment: AlignCenter;
            }}
            QLabel#urllabel {{
                background-color: {darker_color.name()};
                border: 1px solid white;
                border-radius: 12px;
                padding: 3px;
                font-size: 16px;
                qproperty-alignment: AlignCenter;
            }}
            QCheckBox {{
                spacing: 12px;
                font-size: 16px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid white;
                background-color: transparent;
            }}
            QCheckBox::indicator:checked {{
                background-color: white;
            }}
            QLineEdit {{
                background-color: #333;
                border: 2px solid white;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
            }}
            QPushButton {{
                background-color: gray;
                border: 1px solid white;
                border-radius: 12px;
                padding: 12px;
                font-size: 18px;
                font-weight: bold;
                color: white;
            }}
            QPushButton:hover {{
                background-color: {darker_color.name()};
            }}
            QPushButton:pressed {{
                background-color: #000;
            }}
            QPushButton#updateButton {{
                border: 1px solid white;
                border-radius: 6px;
                padding: 0px;
                margin: 0;
                background-color: transparent;
                min-width: 40px;
                max-width: 40px;
                min-height: 40px;
                max-height: 40px;
            }}
            QPushButton#updateButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
            }}
            QPushButton#updateButton:pressed {{
                background-color: rgba(0, 0, 0, 0.2);
            }}
        """)

        # Create main container for content
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)
        
        # Create a container for the upper part (everything except buttons)
        upper_container = QWidget()
        upper_layout = QVBoxLayout(upper_container)
        upper_layout.setContentsMargins(0, 0, 0, 0)
        upper_layout.setSpacing(15)

        # Add heading
        self.heading = QLabel("SHITTY YTDLP HELPER")
        self.heading.setObjectName("heading")
        main_layout.addWidget(self.heading)

        # Add URL input
        self.urllabel = QLabel("ENTER VIDEO URL")
        self.urllabel.setObjectName("urllabel")
        main_layout.addWidget(self.urllabel)

        self.url_input = QLineEdit()
        main_layout.addWidget(self.url_input)

        # Create a horizontal layout for checkboxes and image
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # Left side - checkboxes
        checkboxes_layout = QVBoxLayout()
        checkboxes_layout.setSpacing(8)
        
        # Add checkboxes
        self.best_quality = QCheckBox("Best Quality")
        self.best_quality.setChecked(True)  # Default ON
        self.mp4_output = QCheckBox("MP4 Output")
        self.mp4_output.setChecked(True)  # Default ON
        self.pretty_naming = QCheckBox("Pretty Naming")
        self.pretty_naming.setChecked(True)  # Default ON
        self.audio_only = QCheckBox("Audio Only")
        self.embed_subs = QCheckBox("Embed Subtitles")
        self.ffmpeg_check = QCheckBox("Use FFmpeg (if available)")
        self.ffmpeg_check.setChecked(True)  # Keep FFmpeg ON by default
        
        self.auto_close_terminal = QCheckBox("Auto-Close Terminal")
        self.auto_close_terminal.setChecked(True)

        checkboxes_layout.addWidget(self.best_quality)
        checkboxes_layout.addWidget(self.mp4_output)
        checkboxes_layout.addWidget(self.pretty_naming)
        checkboxes_layout.addWidget(self.audio_only)
        checkboxes_layout.addWidget(self.embed_subs)
        checkboxes_layout.addWidget(self.ffmpeg_check)
        checkboxes_layout.addWidget(self.auto_close_terminal)
        checkboxes_layout.addStretch()
        
        # Add checkboxes to content layout
        content_layout.addLayout(checkboxes_layout)
        
        # Add image to the right of checkboxes
        self.image_label = ClickableLabel()
        self.image_label.setCursor(Qt.PointingHandCursor)
        
        # Ensure downloads directory exists (already set in __init__)
        
        # Load and set up the image with error handling
        try:
            image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rc', 'SYHSB.png')
            pixmap = QPixmap(image_path)
            
            if pixmap.isNull():
                raise ValueError(f"Failed to load image: {image_path}")
            
            # Calculate size to fit the space
            checkbox_height = (7 * 24) + (6 * 8)  # 7 checkboxes * 24px height + 6 gaps * 8px
            max_width = 200
            min_size = 32  # Minimum size to prevent division by zero
            
            # Ensure we have valid dimensions
            if pixmap.width() <= 0 or pixmap.height() <= 0:
                raise ValueError(f"Invalid image dimensions: {pixmap.width()}x{pixmap.height()}")
            
            # Calculate aspect ratio safely
            aspect_ratio = max(0.1, pixmap.width() / max(pixmap.height(), 1))
            height = max(min_size, checkbox_height)
            width = max(min_size, int(height * aspect_ratio))
            
            if width > max_width:
                width = max(max_width, min_size)
                height = max(min_size, int(width / max(aspect_ratio, 0.1)))
            
            # Scale using device pixel ratio for better quality
            device_pixel_ratio = max(1.0, self.devicePixelRatio())
            scaled_pixmap = pixmap.scaled(
                max(1, int(width * device_pixel_ratio)),
                max(1, int(height * device_pixel_ratio)),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            if not scaled_pixmap.isNull():
                scaled_pixmap.setDevicePixelRatio(device_pixel_ratio)
                self.image_label.setPixmap(scaled_pixmap)
                self.image_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
                self.image_label.setFixedSize(max(1, width), max(1, height))
            
        except Exception as e:
            print(f"Error loading image: {e}")
            # Set a default minimum size to prevent layout issues
            self.image_label.setFixedSize(100, 100)
            self.image_label.setText("Image not found")
            self.image_label.setStyleSheet("color: white; background-color: transparent;")
        
        # Connect double-click signal to open downloads folder
        self.image_label.doubleClicked.connect(self.open_downloads_folder)
        
        # Add image to content layout with stretch to push it to the right
        content_layout.addStretch()
        content_layout.addWidget(self.image_label, 0, Qt.AlignRight | Qt.AlignTop)
        
        # Add content layout to upper container
        upper_layout.addLayout(content_layout)
        
        # Add upper container to main layout with stretch to push it to the top
        main_layout.addWidget(upper_container, 1)  # Takes all available space
        
        # Create button container with fixed height
        button_container = QWidget()
        button_container.setFixedHeight(45)
        
        # Use a horizontal layout for the buttons
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)  # Space between buttons
        
        # Main action button (GET 'EM) - takes 4/5 of the width
        self.button = QPushButton("GET 'EM")
        self.button.setMinimumHeight(40)
        self.button.clicked.connect(self.download)
        
        # Update button (smaller, to the right) - takes 1/5 of the width
        self.update_button = QPushButton()
        self.update_button.setObjectName("updateButton")
        self.update_button.clicked.connect(self.perform_update)
        
        # Set initial icon and size
        self.update_button.setFixedSize(40, 40)
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rc", "update_icon_gray.png")
        if os.path.exists(icon_path):
            # Load and scale the icon to fill the button
            pixmap = QPixmap(icon_path).scaled(
                38, 38,  # Slightly smaller than button to account for border
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Create a new pixmap with transparent background
            result = QPixmap(40, 40)
            result.fill(Qt.GlobalColor.transparent)
            
            # Draw the icon centered
            painter = QPainter(result)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            
            # Draw the icon
            painter.drawPixmap(1, 1, pixmap)  # Offset by 1px to account for border
            painter.end()
            
            self.update_button.setIcon(QIcon(result))
            self.update_button.setIconSize(QSize(40, 40))  # Match button size
        
        # Add buttons to layout with stretch factors
        button_layout.addWidget(self.button, 4)  # 4/5 of the space
        button_layout.addWidget(self.update_button, 1)  # 1/5 of the space
        
        # Add button container to main layout with fixed position at the bottom
        main_layout.addSpacing(20)  # Add some space above the buttons
        main_layout.addWidget(button_container, 0, Qt.AlignBottom)
        main_layout.addSpacing(10)  # Add some space below the buttons
        
        # Set the main layout
        self.setLayout(main_layout)
        
        # Set focus to URL input box for better UX after window is shown
        QTimer.singleShot(100, lambda: self.url_input.setFocus())

    def download(self):
        """Handle the download button click event."""
        url = self.url_input.text().strip()
        if not url:
            self.show_custom_message("Error", "Please enter a video URL.")
            return

        args = []
        
        # Handle the quality/format selection
        if self.audio_only.isChecked() and self.best_quality.isChecked():
            # If both are checked, default to audio-only (more specific use case)
            self.show_custom_message(
                "Info",
                "Both 'Best Quality' and 'Audio Only' were selected.\n"
                "Defaulting to 'Audio Only' for best results."
            )
            args.extend(["-x", "--audio-format", "mp3"])
        elif self.audio_only.isChecked():
            args.extend(["-x", "--audio-format", "mp3"])
        elif self.best_quality.isChecked():
            args.extend(["-f", "bestvideo+bestaudio"])
        
        if self.mp4_output.isChecked() and not self.audio_only.isChecked():
            args.extend(["--merge-output-format", "mp4"])
        
        # Set output template
        if self.pretty_naming.isChecked():
            output_template = os.path.join(self.downloads_dir, '%(title)s.%(ext)s')
        else:
            output_template = os.path.join(self.downloads_dir, '%(title)s-%(id)s.%(ext)s')
            
        args.extend(['-o', output_template])
        
        if self.embed_subs.isChecked():
            args.append("--embed-subs")
        
        # Add the URL at the end
        args.append(url)
        
        # Build the command
        cmd = ["yt-dlp"] + args
        
        # Run the command in a new terminal window
        try:
            if platform.system() == "Windows":
                if self.auto_close_terminal.isChecked():
                    # On Windows with auto-close, run directly in a new console
                    subprocess.Popen(
                        cmd,
                        creationflags=subprocess.CREATE_NEW_CONSOLE,
                        cwd=self.project_dir
                    )
                else:
                    # On Windows without auto-close, use cmd /k to keep terminal open
                    subprocess.Popen(
                        ["cmd", "/k"] + cmd,
                        creationflags=subprocess.CREATE_NEW_CONSOLE,
                        cwd=self.project_dir
                    )
            else:
                # For Linux/macOS
                if self.auto_close_terminal.isChecked():
                    # Close terminal automatically after completion
                    terminal_cmd = " ".join(cmd)
                else:
                    # Keep terminal open and wait for key press
                    terminal_cmd = " ".join(cmd) + "; echo 'Press any key to close...'; read -n1"
                
                # Try different terminal emulators
                terminals = ["x-terminal-emulator", "gnome-terminal", "konsole", "xterm"]
                terminal_found = False
                
                for term in terminals:
                    try:
                        subprocess.Popen(
                            [term, "-e", "bash", "-c", terminal_cmd],
                            cwd=self.project_dir  # Run from project dir so yt-dlp and ffmpeg are found
                        )
                        terminal_found = True
                        break
                    except FileNotFoundError:
                        continue
                
                if not terminal_found:
                    raise Exception("No terminal emulator found. Please install x-terminal-emulator, gnome-terminal, konsole, or xterm.")
            
            # Clear the URL input after successful download start
            self.url_input.clear()
            
        except Exception as e:
            self.show_custom_message("Error", f"Could not start download:\n{e}")
    
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        quit_action = menu.addAction("Exit")
        quit_action.triggered.connect(self.quit_application)
        menu.exec(QCursor.pos())

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.pos()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.drag_pos is not None:
            new_pos = event.globalPosition().toPoint() - self.drag_pos
            snapped_pos = self.apply_snapping(new_pos)
            self.move(snapped_pos)
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        self.drag_pos = None
        self.unsetCursor()

    def apply_snapping(self, pos):
        # Get the screen that contains the current window
        screen = QApplication.screenAt(pos)
        if not screen:
            screen = QApplication.primaryScreen()
        screen_geo = screen.geometry()
        
        window_rect = self.geometry()
        window_rect.moveTo(pos)
        
        new_x, new_y = pos.x(), pos.y()
        window_width = window_rect.width()
        window_height = window_rect.height()
        
        # Calculate distances to screen edges
        left_dist = abs(new_x - screen_geo.left())
        right_dist = abs((screen_geo.right() - new_x - window_width))
        top_dist = abs(new_y - screen_geo.top())
        bottom_dist = abs((screen_geo.bottom() - new_y - window_height))
        
        # Snap to screen edges
        if left_dist <= self.snap_threshold:
            new_x = screen_geo.left()
        elif right_dist <= self.snap_threshold:
            new_x = screen_geo.right() - window_width + 1  # +1 to avoid off-by-one
            
        if top_dist <= self.snap_threshold:
            new_y = screen_geo.top()
        elif bottom_dist <= self.snap_threshold:
            new_y = screen_geo.bottom() - window_height + 1  # +1 to avoid off-by-one
        
        # Also snap to screen center (vertical)
        screen_center_x = screen_geo.center().x()
        if abs((new_x + window_width // 2) - screen_center_x) <= self.snap_threshold:
            new_x = screen_center_x - window_width // 2
        
        return QPoint(new_x, new_y)

    def start_update_check(self):
        """Start the update check in a background thread"""
        if not hasattr(self, 'update_button') or not self.update_button:
            QTimer.singleShot(1000, self.start_update_check)  # Try again in 1 second
            return
            
        # Connect signal only once
        if not hasattr(self, '_update_signal_connected'):
            self.update_button_signal.connect(self.style_update_button)
            self._update_signal_connected = True
            
        threading.Thread(target=self.check_for_update, daemon=True).start()
    
    def check_for_update(self):
        """Check for yt-dlp updates in a background thread"""
        try:
            print("Checking for yt-dlp updates...")
            api = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
            r = requests.get(api, timeout=5)
            if not r.ok:
                print(f"Failed to check for updates: HTTP {r.status_code}")
                return
                
            data = r.json()
            self.latest_version = data.get("tag_name")
            print(f"Latest version on GitHub: {self.latest_version}")
            
            for asset in data.get("assets", []):
                if asset.get("name") == "yt-dlp.exe":
                    self.download_url = asset.get("browser_download_url")
                    break
                    
            local_ver = None
            try:
                cmd = ["yt-dlp.exe" if platform.system()=="Windows" else "yt-dlp", "--version"]
                run_args = {"capture_output": True, "text": True}
                if platform.system() == "Windows":
                    run_args["creationflags"] = subprocess.CREATE_NO_WINDOW
                out = subprocess.run(cmd, **run_args)
                if out.returncode == 0:
                    local_ver = out.stdout.strip()
                    print(f"Local yt-dlp version: {local_ver}")
            except Exception as e:
                print(f"Failed to get local yt-dlp version: {e}")
                
            self.update_available = (local_ver is None or local_ver != self.latest_version)
            print(f"Update available: {self.update_available}")
            
            # Use signal to update the UI from the main thread
            self.update_button_signal.emit()
            
        except Exception as e:
            print(f"Update check failed: {e}")
            import traceback
            traceback.print_exc()
    
    def style_update_button(self):
        """Update the style of the update button with consistent icon handling"""
        try:
            if not hasattr(self, 'update_button') or not self.update_button:
                print("Update button not initialized yet")
                return
                
            # Both icons are 1024x1024 and should be treated identically
            icon_file = "update_icon.png" if self.update_available else "update_icon_gray.png"
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rc", icon_file)
            
            if not os.path.exists(icon_path):
                print(f"Icon not found: {icon_path}")
                return
            
            # Get the device pixel ratio for high-DPI displays
            screen = self.screen()
            pixel_ratio = screen.devicePixelRatio() if screen else 1.0
            
            # Button size (40x40)
            button_size = QSize(40, 40)
            
            # Create the target pixmap
            result = QPixmap(button_size * pixel_ratio)
            result.setDevicePixelRatio(pixel_ratio)
            result.fill(Qt.GlobalColor.transparent)
            
            # Load and scale the icon
            pixmap = QPixmap(icon_path)
            if pixmap.isNull():
                print(f"Failed to load icon: {icon_path}")
                return
                
            # Scale to fill the entire button (40x40)
            scaled_size = button_size * pixel_ratio
            scaled_pixmap = pixmap.scaled(
                scaled_size,
                Qt.AspectRatioMode.IgnoreAspectRatio,  # Fill the entire area
                Qt.TransformationMode.SmoothTransformation
            )
            scaled_pixmap.setDevicePixelRatio(pixel_ratio)
            
            # Fill the entire button
            x_offset = 0
            y_offset = 0
            
            # Create a clipping path with rounded corners (4px radius to match button style)
            path = QPainterPath()
            path.addRoundedRect(0, 0, button_size.width(), button_size.height(), 4, 4)
            
            # Draw the icon with clipping
            painter = QPainter(result)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            
            # Set the clipping path
            painter.setClipPath(path)
            
            # Draw the icon (it will be clipped to the rounded rectangle)
            painter.drawPixmap(
                QPointF(x_offset, y_offset),
                scaled_pixmap
            )
            painter.end()
            
            # Set the button properties
            self.update_button.setIcon(QIcon(result))
            self.update_button.setIconSize(button_size)
            self.update_button.setFixedSize(button_size)
            
            # Update tooltip
            tooltip = "Check for yt-dlp updates"
            if self.update_available and self.latest_version:
                tooltip = f"Update available: {self.latest_version}"
            self.update_button.setToolTip(tooltip)
            
            # Force style refresh
            self.update_button.style().unpolish(self.update_button)
            self.update_button.style().polish(self.update_button)
            self.update_button.update()
            
        except Exception as e:
            print(f"Error styling update button: {e}")
            import traceback
            traceback.print_exc()
    
    def perform_update(self):
        """Download and install the latest yt-dlp version."""
        if not self.download_url:
            self.show_custom_message("Error", "Could not fetch yt-dlp release information.", is_error=True)
            return
            
        if not self.update_available:
            # Create a custom dialog for update confirmation
            dialog = QDialog()
            dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
            dialog.setAttribute(Qt.WA_TranslucentBackground)
            dialog.setFixedSize(400, 150)
            
            # Main container
            container = QWidget(dialog)
            container.setObjectName("container")
            container.setStyleSheet("""
                QWidget#container {
                    background-color: #2a2a2a;
                    border: 3px solid white;
                    border-radius: 15px;
                }
                QLabel {
                    color: white;
                    font-size: 16px;
                    padding: 10px;
                }
                QPushButton {
                    background-color: #444;
                    color: white;
                    border: 1px solid white;
                    border-radius: 10px;
                    padding: 6px 12px;
                    min-width: 80px;
                    margin: 5px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #555;
                }
            """)
            
            # Layout
            layout = QVBoxLayout(container)
            
            # Message
            message = QLabel("No new version found. Redownload current version?")
            message.setWordWrap(True)
            message.setAlignment(Qt.AlignCenter)
            layout.addWidget(message, 1)
            
            # Buttons
            button_box = QHBoxLayout()
            yes_button = QPushButton("Yes")
            no_button = QPushButton("No")
            
            def on_yes():
                dialog.done(1)
                
            def on_no():
                dialog.done(0)
                
            yes_button.clicked.connect(on_yes)
            no_button.clicked.connect(on_no)
            
            button_box.addStretch()
            button_box.addWidget(yes_button)
            button_box.addWidget(no_button)
            button_box.addStretch()
            
            layout.addLayout(button_box)
            
            # Set layout and show
            dialog.setLayout(QVBoxLayout())
            dialog.layout().addWidget(container)
            dialog.layout().setContentsMargins(30, 30, 30, 30)
            
            # Center on screen
            dialog.move(
                self.x() + (self.width() - dialog.width()) // 2,
                self.y() + (self.height() - dialog.height()) // 2
            )
            
            if dialog.exec() != 1:
                return
        
        try:
            # Show download progress
            msg = QDialog(self)
            msg.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
            msg.setAttribute(Qt.WA_TranslucentBackground)
            msg.setFixedSize(400, 150)
            
            # Main container
            container = QWidget(msg)
            container.setObjectName("container")
            container.setStyleSheet("""
                QWidget#container {
                    background-color: #2a2a2a;
                    border: 3px solid white;
                    border-radius: 15px;
                    padding: 20px;
                }
                QLabel {
                    color: white;
                    font-size: 16px;
                    padding: 10px;
                    text-align: center;
                }
            """)
            
            # Layout
            layout = QVBoxLayout(container)
            
            # Message
            message = QLabel("Downloading the latest version of yt-dlp...")
            message.setWordWrap(True)
            message.setAlignment(Qt.AlignCenter)
            
            # Add message to layout
            layout.addWidget(message)
            
            # Set layout
            container.setLayout(layout)
            
            # Center on screen
            msg.move(
                self.x() + (self.width() - msg.width()) // 2,
                self.y() + (self.height() - msg.height()) // 2
            )
            
            msg.show()
            QApplication.processEvents()
            
            # Download the file
            r = requests.get(self.download_url, stream=True, timeout=10)
            if r.status_code == 200:
                temp_file = "yt-dlp.tmp"
                with open(temp_file, "wb") as f:
                    shutil.copyfileobj(r.raw, f)
                
                # Replace the existing file
                target_file = "yt-dlp.exe" if platform.system() == "Windows" else "yt-dlp"
                if os.path.exists(target_file):
                    backup_file = f"{target_file}.old"
                    if os.path.exists(backup_file):
                        os.remove(backup_file)
                    os.rename(target_file, backup_file)
                
                os.rename(temp_file, target_file)
                
                # On Unix-like systems, make the file executable
                if platform.system() != "Windows":
                    os.chmod(target_file, 0o755)
                
                msg.close()
                self.show_custom_message("Update Complete", "yt-dlp has been successfully updated!")
                self.update_available = False
                self.style_update_button()
                
            else:
                msg.close()
                self.show_custom_message("Download Failed", "Failed to download the latest version.", is_error=True)
                
        except Exception as e:
            if 'msg' in locals():
                msg.close()
            self.show_custom_message("Update Error", f"An error occurred: {str(e)}", is_error=True)
            self.url_input.setFocus()

    def show_custom_message(self, title, message, is_error=False):
        """Show a custom styled message box without titlebar
        
        Args:
            title (str): The window title
            message (str): The message to display
            is_error (bool): If True, shows error icon and styles accordingly
        """
        # Create a custom dialog
        dialog = QDialog()
        dialog.setWindowTitle(title)
        
        # Set window flags for frameless window with drop shadow
        dialog.setWindowFlags(
            Qt.Dialog | 
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.WindowSystemMenuHint |
            Qt.WindowCloseButtonHint
        )
        
        # Enable window transparency and set attributes
        dialog.setAttribute(Qt.WA_TranslucentBackground)
        dialog.setAttribute(Qt.WA_ShowWithoutActivating)
        dialog.setFixedSize(400, 200)
        
        # Make sure the dialog is modal
        dialog.setModal(True)
        
        # Ensure the dialog is shown on the active screen
        dialog.activateWindow()
        dialog.raise_()
        
        # Main container with border radius
        container = QWidget(dialog)
        container.setObjectName("container")
        container.setGeometry(0, 0, 400, 200)
        
        # Layout for the dialog
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title label
        title_label = QLabel(f"<h3>{title}</h3>")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #ff6600;
                font-size: 16px;
                font-weight: bold;
                padding-bottom: 10px;
                border-bottom: 1px solid #444;
                margin-bottom: 10px;
            }
        """)
        
        # Message label
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setAlignment(Qt.AlignCenter)
        msg_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                padding: 10px;
            }
        """)
        
        # OK button
        ok_btn = QPushButton("OK")
        ok_btn.setFixedSize(100, 30)
        ok_btn.clicked.connect(dialog.accept)
        
        # Add widgets to layout
        layout.addWidget(title_label)
        layout.addWidget(msg_label, 1)  # Allow message to expand
        
        # Button container to center the OK button
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 10, 0, 0)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addStretch()
        
        layout.addWidget(btn_container)
        
        # Set stylesheet for the dialog
        dialog.setStyleSheet("""
            QDialog {
                background: transparent;
            }
            #container {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 10px;
            }
            QPushButton {
                background-color: #444;
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px 15px;
                min-width: 80px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #555;
            }
            QPushButton:pressed {
                background-color: #666;
            }
        """)
        
        def show_dialog():
            # Center the dialog on the parent window
            parent_rect = self.geometry()
            dialog.move(
                parent_rect.left() + (parent_rect.width() - dialog.width()) // 2,
                parent_rect.top() + (parent_rect.height() - dialog.height()) // 2
            )
            # Show the dialog
            dialog.show()
            dialog.activateWindow()
            dialog.raise_()
        
        # Use a single-shot timer to ensure the dialog is properly positioned and shown
        QTimer.singleShot(10, show_dialog)
        
        # Start the dialog's event loop
        dialog.exec()
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self.quit_application()
        super().keyPressEvent(event)
    
    def quit_application(self):
        """Clean up and quit the application."""
        # Close any open dialogs
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QDialog) and widget.isVisible():
                widget.reject()
        
        # Stop any running processes
        if hasattr(self, 'process') and self.process:
            try:
                if self.process.state() == QProcess.Running:
                    self.process.terminate()
                    if not self.process.waitForFinished(2000):  # Wait up to 2 seconds
                        self.process.kill()
            except Exception as e:
                print(f"Error terminating process: {e}")
        
        # Clean up temporary files if any
        if hasattr(self, 'temp_files') and self.temp_files:
            for temp_file in self.temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception as e:
                    print(f"Error removing temporary file {temp_file}: {e}")
        
        # Save any settings if needed
        if hasattr(self, 'settings') and self.settings:
            try:
                self.settings.sync()
            except Exception as e:
                print(f"Error saving settings: {e}")
        
        # Quit the application
        QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set application properties for taskbar and window manager
    app.setApplicationName("SYH")
    app.setApplicationDisplayName("SYH")
    app.setDesktopFileName("SYH")  # For Linux
    
    window = ShittyYTDLPHelper()
    window.setWindowTitle("SYH - Shitty YTDLP Helper")
    window.resize(420, 620)  # Increased height from 520px to 620px
    window.show()
    sys.exit(app.exec())