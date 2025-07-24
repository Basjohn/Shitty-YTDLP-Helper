import sys
import subprocess
import platform
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QCheckBox, QLineEdit, QPushButton, QMenu, QMessageBox
)
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QCursor, QMouseEvent, QColor, QPainter

class ShittyYTDLPHelper(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
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
                border-radius: 15px;
                padding: 10px;
                qproperty-alignment: AlignCenter;
            }}
            QLabel#urllabel {{
                background-color: {darker_color.name()};
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
                border: none;
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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)  # Account for border
        layout.setSpacing(15)

        self.heading = QLabel("SHITTY YTDLP HELPER")
        self.heading.setObjectName("heading")
        layout.addWidget(self.heading)

        self.urllabel = QLabel("ENTER VIDEO URL")
        self.urllabel.setObjectName("urllabel")
        layout.addWidget(self.urllabel)

        self.url_input = QLineEdit()
        layout.addWidget(self.url_input)

        self.best_quality = QCheckBox("Best Quality")
        self.mp4_output = QCheckBox("MP4 Output")
        self.pretty_naming = QCheckBox("Pretty Naming")
        self.audio_only = QCheckBox("Audio Only")
        self.embed_subs = QCheckBox("Embed Subtitles")
        self.ffmpeg_check = QCheckBox("Use FFmpeg (if available)")
        self.ffmpeg_check.setChecked(True)

        layout.addWidget(self.best_quality)
        layout.addWidget(self.mp4_output)
        layout.addWidget(self.pretty_naming)
        layout.addWidget(self.audio_only)
        layout.addWidget(self.embed_subs)
        layout.addWidget(self.ffmpeg_check)

        self.button = QPushButton("GET 'EM")
        self.button.clicked.connect(self.download)
        layout.addWidget(self.button)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        quit_action = menu.addAction("Exit")
        quit_action.triggered.connect(self.quit_application)
        menu.exec(QCursor.pos())

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.drag_pos:
            delta = event.globalPosition().toPoint() - self.drag_pos
            new_pos = self.pos() + delta
            snapped_pos = self.apply_snapping(new_pos)
            self.move(snapped_pos)
            # Update drag_pos to the new global position to prevent sticking
            self.drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.drag_pos = None

    def apply_snapping(self, pos):
        screen = QApplication.primaryScreen().geometry()
        window_rect = self.geometry()
        
        new_x = pos.x()
        new_y = pos.y()
        window_width = window_rect.width()
        window_height = window_rect.height()
        
        if abs(new_x) <= self.snap_threshold:
            new_x = 0
        if abs(new_x + window_width - screen.width()) <= self.snap_threshold:
            new_x = screen.width() - window_width
        if abs(new_y) <= self.snap_threshold:
            new_y = 0
        if abs(new_y + window_height - screen.height()) <= self.snap_threshold:
            new_y = screen.height() - window_height
        
        return QPoint(new_x, new_y)

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2,
                  (screen.height() - size.height()) // 2)

    def download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Missing URL", "Please enter a video URL.")
            return

        args = []
        if self.best_quality.isChecked():
            args += ["-f", "bestvideo+bestaudio"]
        elif self.audio_only.isChecked():
            args += ["-f", "bestaudio"]
            
        if self.mp4_output.isChecked():
            args += ["--merge-output-format", "mp4"]
            
        if self.pretty_naming.isChecked():
            args += ["-o", "%(title)s.%(ext)s"]

        if self.embed_subs.isChecked():
            args += ["--embed-subs"]

        if self.ffmpeg_check.isChecked():
            for path in ["ffmpeg.exe", "./ffmpeg/ffmpeg.exe", "./ffmpeg"]:
                if os.path.exists(path):
                    args += ["--ffmpeg-location", path]
                    break

        yt_dlp_cmd = "yt-dlp.exe" if platform.system() == "Windows" else "yt-dlp"

        try:
            subprocess.check_output([yt_dlp_cmd, "--version"])
        except (FileNotFoundError, subprocess.CalledProcessError):
            QMessageBox.critical(
                self,
                "yt-dlp Not Found",
                f"Could not find '{yt_dlp_cmd}' in PATH.\n\nMake sure yt-dlp is installed and accessible."
            )
            return

        full_cmd = [yt_dlp_cmd] + args + [url]

        try:
            if platform.system() == "Windows":
                subprocess.Popen(["cmd", "/k"] + full_cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                cmd_with_pause = full_cmd + [";", "echo", "Press any key to close...;", "read", "-n1"]
                subprocess.Popen(["x-terminal-emulator", "-e", "bash", "-c", " ".join(cmd_with_pause)])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not run command:\n{e}")

    def quit_application(self):
        QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ShittyYTDLPHelper()
    window.resize(420, 520)
    window.show()
    sys.exit(app.exec())