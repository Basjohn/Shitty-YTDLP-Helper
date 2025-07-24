import sys
import subprocess
import platform
import os
import webbrowser
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QCheckBox, QLineEdit, QPushButton, QMenu, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt, QPoint, QTimer, QSize, Signal
from PySide6.QtGui import QCursor, QMouseEvent, QColor, QPainter, QIcon, QPixmap

class ClickableLabel(QLabel):
    doubleClicked = Signal()
    
    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)


class ShittyYTDLPHelper(QWidget):
    VERSION = "1.11a"
    
    def open_downloads_folder(self):
        """Open the downloads folder in the system file explorer."""
        try:
            if platform.system() == "Windows":
                os.startfile(self.downloads_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", self.downloads_dir])
            else:  # Linux and other Unix-like
                subprocess.Popen(["xdg-open", self.downloads_dir])
        except Exception as e:
            print(f"Error opening downloads folder: {e}")

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
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle(f"Shitty YTDLP Helper v{self.VERSION}")
        # Set application and window icons for taskbar
        icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rc')
        icon_ext = '.ico' if platform.system() == 'Windows' else '.png'
        icon_path = os.path.join(icon_dir, f'SYHSB{icon_ext}')
        
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            QApplication.setWindowIcon(app_icon)
            self.setWindowIcon(app_icon)
        
        self.drag_pos = None
        self.snap_threshold = 20

        self.init_ui()
        QTimer.singleShot(100, self.center_on_screen)

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
        """)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)

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
        
        # Store downloads directory path for opening on click
        self.downloads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
        os.makedirs(self.downloads_dir, exist_ok=True)
        
        # Load and set up the image
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rc', 'SYHSB.png')
        pixmap = QPixmap(image_path)
        
        # Calculate size to fit the space
        checkbox_height = (6 * 24) + (5 * 8)  # 6 checkboxes * 24px height + 5 gaps * 8px
        max_width = 200
        
        # Maintain aspect ratio
        aspect_ratio = pixmap.width() / pixmap.height()
        height = checkbox_height
        width = int(height * aspect_ratio)
        
        if width > max_width:
            width = max_width
            height = int(width / aspect_ratio)
        
        # Scale using device pixel ratio for better quality
        device_pixel_ratio = self.devicePixelRatio()
        scaled_pixmap = pixmap.scaled(
            int(width * device_pixel_ratio),
            int(height * device_pixel_ratio),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        scaled_pixmap.setDevicePixelRatio(device_pixel_ratio)
        
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.image_label.setFixedSize(width, height)
        
        # Connect double-click signal to open downloads folder
        self.image_label.doubleClicked.connect(self.open_downloads_folder)
        
        # Add image to content layout with stretch to push it to the right
        content_layout.addStretch()
        content_layout.addWidget(self.image_label, 0, Qt.AlignRight | Qt.AlignTop)
        
        # Add content layout to main layout
        main_layout.addLayout(content_layout)
        
        # Add the button below everything
        self.button = QPushButton("GET 'EM")
        self.button.clicked.connect(self.download)
        main_layout.addWidget(self.button)
        
        # Set the main layout
        self.setLayout(main_layout)
        
        # Set focus to URL input box for better UX
        self.url_input.setFocus()

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

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2,
                  (screen.height() - size.height()) // 2)

    def download(self):
        url = self.url_input.text().strip()
        if not url:
            self.show_custom_message("Please enter a video URL.")
            return

        args = []
        
        # Handle the quality/format selection
        if self.audio_only.isChecked() and self.best_quality.isChecked():
            # If both are checked, default to audio-only (more specific use case)
            self.show_custom_message(
                "Both 'Best Quality' and 'Audio Only' were selected.\n"
                "Defaulting to 'Audio Only' for best results."
            )
            args.append("-x")  # Extract audio
            args.append("--audio-format")
            args.append("mp3")
        elif self.audio_only.isChecked():
            args.append("-x")  # Extract audio
            args.append("--audio-format")
            args.append("mp3")
        elif self.best_quality.isChecked():
            args.extend(["-f", "bestvideo+bestaudio"])
        
        if self.mp4_output.isChecked() and not self.audio_only.isChecked():
            args.append("--merge-output-format")
            args.append("mp4")
        
        # Create downloads directory relative to the executable/script
        base_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
        downloads_dir = os.path.join(base_dir, 'downloads')
        os.makedirs(downloads_dir, exist_ok=True)
        
        # Set output template
        if self.pretty_naming.isChecked():
            output_template = os.path.join(downloads_dir, '%(title)s.%(ext)s')
        else:
            output_template = os.path.join(downloads_dir, '%(title)s-%(id)s.%(ext)s')
            
        args.extend(['-o', output_template])
        
        if self.embed_subs.isChecked():
            args.append("--embed-subs")
        
        if self.ffmpeg_check.isChecked():
            # Check for ffmpeg in the script directory first, then in system PATH
            script_dir = os.path.dirname(os.path.abspath(__file__))
            ffmpeg_path = "ffmpeg"  # Default to system PATH
            
            # Look for ffmpeg in the script directory
            # Check for ffmpeg in multiple locations in order of preference
            script_dir = os.path.dirname(os.path.abspath(__file__))
            ffmpeg_path = None
            
            # 1. Try in the script/exe directory
            if platform.system() == "Windows":
                possible_paths = [
                    os.path.join(script_dir, "ffmpeg.exe"),  # Same directory as exe
                    os.path.join(script_dir, "ffmpeg", "ffmpeg.exe"),  # In ffmpeg subfolder
                    "ffmpeg.exe"  # System PATH as last resort
                ]
            else:
                possible_paths = [
                    os.path.join(script_dir, "ffmpeg"),  # Same directory as script
                    os.path.join(script_dir, "ffmpeg", "ffmpeg"),  # In ffmpeg subfolder
                    "/usr/bin/ffmpeg",  # Common Linux location
                    "/usr/local/bin/ffmpeg",  # Common macOS/alternative Linux location
                    "ffmpeg"  # System PATH as last resort
                ]
            
            # Find the first valid path
            for path in possible_paths:
                if os.path.isfile(path):
                    ffmpeg_path = path
                    break
            
            # If no valid path found, use the first one as default (will show error if not in PATH)
            if not ffmpeg_path:
                ffmpeg_path = possible_paths[0]
            
            args.extend(["--ffmpeg-location", ffmpeg_path])
        
        # Add the URL at the end
        args.append(url)
        
        # Build the command
        cmd = ["yt-dlp"] + args
        
        # Run the command in a new terminal window
        try:
            if platform.system() == "Windows":
                if self.auto_close_terminal.isChecked():
                    # On Windows with auto-close, use cmd /c to close after completion
                    process = subprocess.Popen(
                        ["cmd", "/c", "start", "", "cmd", "/c"] + cmd,
                        shell=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                else:
                    # Keep terminal open
                    process = subprocess.Popen(
                        ["cmd", "/k"] + cmd,
                        creationflags=subprocess.CREATE_NEW_CONSOLE
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
                terminals = ["x-terminal-emulator", "gnome-terminal", "konsole", "xterm", "terminator"]
                terminal_found = False
                
                for term in terminals:
                    try:
                        if self.auto_close_terminal.isChecked():
                            # Use nohup to prevent terminal from closing immediately
                            process = subprocess.Popen([
                                term, "-e", "bash", "-c", 
                                f"nohup {terminal_cmd} >/dev/null 2>&1 && exit 0 || (echo 'Press any key to close...'; read -n1)"
                            ])
                        else:
                            process = subprocess.Popen([term, "-e", "bash", "-c", terminal_cmd])
                        terminal_found = True
                        break
                    except FileNotFoundError:
                        continue
                
                if not terminal_found:
                    raise Exception(
                        "No terminal emulator found. Please install x-terminal-emulator, "
                        "gnome-terminal, konsole, xterm, or terminator."
                    )
            
            # If we get here, the download process started successfully
            self.url_input.clear()
            self.url_input.setFocus()
                    
        except Exception as e:
            self.show_custom_message(f"Could not run command:\n{e}", is_error=True)
            return

        full_cmd = [yt_dlp_cmd] + args + [url]

        try:
            if platform.system() == "Windows":
                subprocess.Popen(["cmd", "/k"] + full_cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                cmd_with_pause = full_cmd + [";", "echo", "Press any key to close...;", "read", "-n1"]
                subprocess.Popen(["x-terminal-emulator", "-e", "bash", "-c", " ".join(cmd_with_pause)])
        except Exception as e:
            self.show_custom_message(f"Could not run command:\n{e}", is_error=True)

    def show_custom_message(self, message, is_error=False):
        """Show a custom styled message box without titlebar
        
        Args:
            message (str): The message to display
            is_error (bool): If True, shows error icon and styles accordingly
        """
        msg_box = QMessageBox()
        msg_box.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        msg_box.setIcon(QMessageBox.Critical if is_error else QMessageBox.Information)
        msg_box.setText(message)
        
        # Style the message box to match our theme
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2a2a2a;
                color: white;
                border: 3px solid white;
                border-radius: 20px;
                padding: 15px 20px;
                min-width: 300px;
            }
            QMessageBox QLabel#qt_msgbox_label {
                min-width: 250px;
                padding: 10px;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 16px;
                padding: 10px;
            }
            QPushButton {
                background-color: #444444;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:pressed {
                background-color: #666666;
            }
        """)
        
        # Add OK button
        ok_button = msg_box.addButton("OK", QMessageBox.AcceptRole)
        ok_button.setCursor(Qt.PointingHandCursor)
        
        # Show the message box
        msg_box.exec()
    
    def quit_application(self):
        QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set application properties for taskbar and window manager
    app.setApplicationName("Shitty YTDLP Helper")
    app.setApplicationDisplayName("Shitty YTDLP Helper")
    app.setDesktopFileName("shitty-ytdlp-helper")  # For Linux
    
    window = ShittyYTDLPHelper()
    window.setWindowTitle("Shitty YTDLP Helper")
    window.resize(420, 620)  # Increased height from 520px to 620px
    window.show()
    sys.exit(app.exec())