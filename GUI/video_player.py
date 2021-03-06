from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QDir, Qt, QUrl, QSize
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar)

# custom imports:
from GUI.video_frame_grabber import VideoFrameGrabber

class VideoPlayer(QWidget):

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.saving = False
        self.main_window = main_window
        self.setWindowModality(Qt.ApplicationModal)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        btnSize = QSize(16, 16)
        self.videoWidget = QVideoWidget()

        openButton = QPushButton("Open Video")
        openButton.setToolTip("Open Video File")
        openButton.setStatusTip("Open Video File")
        openButton.setFixedHeight(24)
        openButton.setIconSize(btnSize)
        openButton.setFont(QFont("Noto Sans", 8))
        openButton.setIcon(QIcon.fromTheme("document-open", QIcon("D:/_Qt/img/open.png")))
        openButton.clicked.connect(self.abrir)

        captureButton = QPushButton("Capture Current Frame")
        captureButton.setToolTip("Capture the current frame of the video and go back to the main menu.")
        captureButton.setStatusTip("Capture the current frame of the video and go back to the main menu.")
        captureButton.setFixedHeight(24)
        captureButton.setIconSize(btnSize)
        captureButton.setFont(QFont("Noto Sans", 8))
        captureButton.clicked.connect(self.screenshotCall)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(btnSize)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.statusBar = QStatusBar()
        self.statusBar.setFont(QFont("Noto Sans", 7))
        self.statusBar.setFixedHeight(14)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(openButton)
        controlLayout.addWidget(captureButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.addWidget(self.videoWidget)
        layout.addLayout(controlLayout)
        layout.addWidget(self.statusBar)

        self.setLayout(layout)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)
        self.statusBar.showMessage("Ready")

    # inherited callback when the window closes!
    def closeEvent(self, event):
        from GUI.gui_utils import GUIUtils
        print("Close event of video player is called!")
        # GUIUtils.refreshImage(self.main_window, self.main_window.images_dict, self.main_window.label_dict)

    def abrir(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Select a video",
                ".", "Video Files (*.mp4 *.mkv *.flv *.ts *.mts *.avi)")

        if fileName != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)
            self.statusBar.showMessage(fileName)
            self.play()

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()
            self.mediaPlayer.setVideoOutput(self.videoWidget)

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.statusBar.showMessage("Error: " + self.mediaPlayer.errorString())

    def screenshotCall(self):
        #Call video frame grabber
        print("screenshotCall!")
        self.mediaPlayer.pause()


        self.grabber = VideoFrameGrabber(self.videoWidget, self)
        self.mediaPlayer.setVideoOutput(self.grabber)
        print("Frame available", self.grabber.frameAvailable)
        self.grabber.frameAvailable.connect(self.process_frame)


        self.statusBar.showMessage("Taking a screenshot of current frame...")
        # self.mediaPlayer.setVideoOutput(self.grabber)

        # SOMEHOW NEED TO BE LIKE THIS FOR PRESENT TO BE TRIGGERED FOR CIDENG VID...
        import time
        time.sleep(1)
        self.mediaPlayer.pause()


    def process_frame(self, image):
        from GUI.gui_utils import GUIUtils
        # Save image here
        print("process_frame called!")
        if not self.saving: # prevent multiple signals after first saving
            self.saving = True
            self.mediaPlayer.setVideoOutput(self.videoWidget)
            self.mediaPlayer.pause()
            GUIUtils.saveImageDialog(self.main_window, image, cv=False)
            self.statusBar.showMessage("Screenshot successfully saved!")
            self.saving = False


# if __name__ == '__main__':
#     import sys
#     app = QApplication(sys.argv)
#     player = VideoPlayer()
#     player.setWindowTitle("Player")
#     player.resize(600, 400)
#     player.show()
#     sys.exit(app.exec_())