import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QComboBox, QLabel, QFileDialog, QToolBar
from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QIcon, QPainter, QBrush, QColor, QPainterPath, QFont
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

class SciFiButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet("""
            QPushButton {
                background-color: #4B0082;
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFD700;
                color: #4B0082;
            }
        """)

class SubtitleDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.old_pos = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Subtitle Downloader')
        self.setGeometry(300, 300, 500, 250)

        # Custom Title Bar
        title_bar = QWidget(self)
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("""
            QWidget#titleBar {
                background-color: #4B0082;
                border-top-left-radius: 13px;
                border-top-right-radius: 13px;
            }
        """)
        title_bar_layout = QHBoxLayout()
        title_bar_layout.setContentsMargins(0, 0, 0, 0)

        # Window title
        window_title = QLabel("Subtitle Downloader")
        window_title.setStyleSheet("color: #FFD700; padding-left: 10px;")
        title_bar_layout.addWidget(window_title)

        title_bar_layout.addStretch()

        # Minimize button (using text)
        minimize_button = QPushButton("—")
        minimize_button.setFixedSize(30, 30)
        minimize_button.setFont(QFont('Arial', 15, QFont.Bold))
        minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #4B0082; 
                color: #FFD700; 
                border: none;
            }
            QPushButton:hover {
                background-color: #FFD700;
                color: #4B0082;
            }
        """)
        minimize_button.clicked.connect(self.showMinimized)
        title_bar_layout.addWidget(minimize_button)

        # Close button (using text)
        close_button = QPushButton("✕")
        close_button.setFixedSize(30, 30)
        close_button.setFont(QFont('Arial', 15, QFont.Bold))
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #4B0082; 
                color: #FFD700; 
                border: none;
            }
            QPushButton:hover {
                background-color: #FFD700;
                color: #4B0082;
            }
        """)
        close_button.clicked.connect(self.close)
        title_bar_layout.addWidget(close_button)

        title_bar.setLayout(title_bar_layout)

        # Central widget
        central_widget = QWidget(self)
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)

        # Main content area
        content_area = QWidget()
        content_area.setStyleSheet("""
            QWidget {
                background-color: #282828;
                color: #FFFFFF;
                border-bottom-left-radius: 13px;
                border-bottom-right-radius: 13px;
            }
        """)
        layout = QVBoxLayout(content_area)

        # URL input
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        url_layout.addWidget(QLabel("YouTube URL:"))
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # Fetch button
        self.fetch_button = SciFiButton("Fetch Available Subtitles")
        self.fetch_button.clicked.connect(self.fetch_subtitles)
        layout.addWidget(self.fetch_button)

        # Language dropdown
        self.lang_dropdown = QComboBox()
        layout.addWidget(self.lang_dropdown)

        # Download buttons
        button_layout = QHBoxLayout()
        self.download_button = SciFiButton("Download Subtitle")
        self.download_button.clicked.connect(self.download_subtitle)
        button_layout.addWidget(self.download_button)

        self.download_with_timestamp_button = SciFiButton("Download with Timestamps")
        self.download_with_timestamp_button.clicked.connect(self.download_subtitle_with_timestamps)
        button_layout.addWidget(self.download_with_timestamp_button)

        layout.addLayout(button_layout)

        # Status label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Developer info
        info_label = QLabel("Developed by Madson for Eghbal Animation")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #888888; font-style: italic;")
        layout.addWidget(info_label)

        central_layout.addWidget(title_bar)
        central_layout.addWidget(content_area)

        self.setCentralWidget(central_widget)

    def paintEvent(self, event):
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 13, 13)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillPath(path, QBrush(QColor(40, 40, 40)))

    def fetch_subtitles(self):
        try:
            video_id = self.extract_video_id(self.url_input.text())
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            self.lang_dropdown.clear()
            for transcript in transcript_list:
                self.lang_dropdown.addItem(f"{transcript.language} ({transcript.language_code})", transcript.language_code)
            self.status_label.setText("Subtitles fetched successfully")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    def download_subtitle(self):
        try:
            video_id = self.extract_video_id(self.url_input.text())
            language_code = self.lang_dropdown.currentData()
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])
            formatted_transcript = TextFormatter().format_transcript(transcript)

            file_path, _ = QFileDialog.getSaveFileName(self, "Save Subtitle", "", "Text Files (*.txt)")
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(formatted_transcript)
                self.status_label.setText(f"Subtitle saved to {file_path}")
            else:
                self.status_label.setText("Save cancelled")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    def download_subtitle_with_timestamps(self):
        try:
            video_id = self.extract_video_id(self.url_input.text())
            language_code = self.lang_dropdown.currentData()
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])

            formatted_transcript = "\n".join([f"{entry['start']:.2f} --> {entry['start'] + entry['duration']:.2f}\n{entry['text']}" for entry in transcript])

            file_path, _ = QFileDialog.getSaveFileName(self, "Save Subtitle with Timestamps", "", "Text Files (*.txt)")
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(formatted_transcript)
                self.status_label.setText(f"Subtitle with timestamps saved to {file_path}")
            else:
                self.status_label.setText("Save cancelled")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    def extract_video_id(self, url):
        if "youtu.be" in url:
            return url.split("/")[-1]
        elif "youtube.com" in url:
            return url.split("v=")[-1].split("&")[0]
        else:
            raise ValueError("Invalid YouTube URL")

    def mousePressEvent(self, event):
        self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.old_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPos()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = SubtitleDownloader()
    ex.show()
    sys.exit(app.exec_())
