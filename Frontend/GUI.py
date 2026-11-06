from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextEdit,
    QStackedWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFrame,
    QLabel,
    QSizePolicy,
)

from PyQt5.QtGui import (
    QIcon,
    QPainter,
    QMovie,
    QColor,
    QTextCharFormat,
    QFont,
    QPixmap,
    QTextBlockFormat,
)

from PyQt5.QtCore import Qt, QSize, QTimer

from dotenv import dotenv_values

import sys
import os


# =========================================================
# PATH SETUP
# =========================================================

FileDirPath = os.path.dirname(os.path.abspath(__file__))

# If this file is inside Frontend folder
if os.path.basename(FileDirPath).lower() == "frontend":
    current_dir = os.path.dirname(FileDirPath)
else:
    current_dir = FileDirPath


env_vars = dotenv_values(os.path.join(current_dir, ".env"))

Assistantname = env_vars.get("Assistantname") or "Jarvis"

old_chat_message = ""


TempDirPath = os.path.join(
    current_dir,
    "Frontend",
    "Files"
)

GraphicDirPath = os.path.join(
    current_dir,
    "Frontend",
    "Graphics"
)


# Create Files folder if it does not exist
os.makedirs(
    TempDirPath,
    exist_ok=True
)


# Create required files automatically
default_files = {

    "Mic.data": "False",

    "Status.data": "",

    "Responses.data": ""

}


for filename, default_value in default_files.items():

    file_path = os.path.join(
        TempDirPath,
        filename
    )

    if not os.path.exists(file_path):

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(default_value)


# =========================================================
# ANSWER MODIFIER
# =========================================================

def AnswerModifier(Answer):

    lines = Answer.split("\n")

    non_empty_lines = [
        line
        for line in lines
        if line.strip()
    ]

    modified_answer = "\n".join(
        non_empty_lines
    )

    return modified_answer


# =========================================================
# QUERY MODIFIER
# =========================================================

def QueryModifier(Query):

    new_query = Query.lower().strip()

    if not new_query:

        return ""

    query_words = new_query.split()

    question_words = [

        "how",
        "what",
        "who",
        "when",
        "where",
        "why",
        "which",
        "whom",
        "whose",
        "can you",
        "what's",
        "how's"

    ]


    if any(
        word + " " in new_query
        for word in question_words
    ):

        if query_words[-1][-1] in [
            ".",
            ",",
            "?",
            "!"
        ]:

            new_query = new_query[:-1] + "?"

        else:

            new_query += "?"

    else:

        if query_words[-1][-1] in [
            ".",
            "?",
            "!"
        ]:

            new_query = new_query[:-1] + "."

        else:

            new_query += "."


    return new_query.capitalize()


# =========================================================
# MICROPHONE STATUS
# =========================================================

def SetMicrophoneStatus(Command):

    with open(
        TempDirectoryPath("Mic.data"),
        "w",
        encoding="utf-8"
    ) as file:

        file.write(Command)


def GetMicrophoneStatus():

    with open(
        TempDirectoryPath("Mic.data"),
        "r",
        encoding="utf-8"
    ) as file:

        Status = file.read()

    return Status


# =========================================================
# ASSISTANT STATUS
# =========================================================

def SetAssistantStatus(Status):

    with open(
        TempDirectoryPath("Status.data"),
        "w",
        encoding="utf-8"
    ) as file:

        file.write(Status)


def GetAssistantStatus():

    with open(
        TempDirectoryPath("Status.data"),
        "r",
        encoding="utf-8"
    ) as file:

        Status = file.read()

    return Status


# =========================================================
# MIC BUTTON
# =========================================================

def MicButtonInitialed():

    SetMicrophoneStatus("True")


def MicButtonClosed():

    SetMicrophoneStatus("False")


# =========================================================
# PATH FUNCTIONS
# =========================================================

def GraphicsDirectoryPath(Filename):

    return os.path.join(
        GraphicDirPath,
        Filename
    )


def TempDirectoryPath(Filename):

    return os.path.join(
        TempDirPath,
        Filename
    )


# =========================================================
# SHOW TEXT
# =========================================================

def ShowTextToScreen(Text):

    with open(
        TempDirectoryPath("Responses.data"),
        "w",
        encoding="utf-8"
    ) as file:

        file.write(Text)


# =========================================================
# CHAT SECTION
# =========================================================

class ChatSection(QWidget):

    def __init__(self):

        super().__init__()


        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            10,
            20,
            20,
            20
        )

        layout.setSpacing(10)


        # -----------------------------------------
        # CHAT TEXT AREA
        # -----------------------------------------

        self.chat_text_edit = QTextEdit()

        self.chat_text_edit.setReadOnly(True)

        self.chat_text_edit.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )

        self.chat_text_edit.setFrameStyle(
            QFrame.NoFrame
        )


        self.chat_text_edit.setSizePolicy(

            QSizePolicy.Expanding,

            QSizePolicy.Expanding

        )


        font = QFont()

        font.setPointSize(13)

        self.chat_text_edit.setFont(font)


        text_color_text = QTextCharFormat()

        text_color_text.setForeground(
            QColor(Qt.white)
        )

        self.chat_text_edit.setCurrentCharFormat(
            text_color_text
        )


        layout.addWidget(
            self.chat_text_edit,
            stretch=1
        )


        # -----------------------------------------
        # JARVIS GIF
        # -----------------------------------------

        self.gif_label = QLabel()

        self.gif_label.setStyleSheet(
            "border: none;"
        )


        self.gif_label.setAlignment(

            Qt.AlignHCenter
            |
            Qt.AlignBottom

        )


        self.movie = QMovie(

            GraphicsDirectoryPath(
                "Jarvis.gif"
            )

        )


        self.movie.setScaledSize(

            QSize(
                480,
                270
            )

        )


        self.gif_label.setMovie(
            self.movie
        )


        self.movie.start()


        layout.addWidget(

            self.gif_label,

            alignment=Qt.AlignCenter

        )


        # -----------------------------------------
        # STATUS LABEL
        # -----------------------------------------

        self.label = QLabel("")


        self.label.setStyleSheet(

            """
            color: white;
            font-size:16px;
            border:none;
            margin-right:20px;
            """

        )


        self.label.setAlignment(
            Qt.AlignRight
        )


        layout.addWidget(
            self.label
        )


        # -----------------------------------------
        # TIMER
        # -----------------------------------------

        self.timer = QTimer(self)


        self.timer.timeout.connect(
            self.loadMessages
        )


        self.timer.timeout.connect(
            self.SpeechRecogText
        )


        # Changed from 5ms to 100ms
        self.timer.start(100)


        # -----------------------------------------
        # STYLE
        # -----------------------------------------

        self.setStyleSheet(
            """

            QTextEdit {

                background-color: black;

                color: white;

                border: none;

            }


            QScrollBar:vertical {

                border: none;

                background: black;

                width: 10px;

                margin: 0px;

            }


            QScrollBar::handle:vertical {

                background: white;

                min-height: 20px;

            }


            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {

                background: black;

                height: 10px;

            }


            QScrollBar::up-arrow:vertical,
            QScrollBar::down-arrow:vertical {

                border: none;

                background: none;

            }


            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {

                background: none;

            }

            """
        )


    # =====================================================
    # LOAD MESSAGE
    # =====================================================

    def loadMessages(self):

        global old_chat_message


        try:

            with open(

                TempDirectoryPath(
                    "Responses.data"
                ),

                "r",

                encoding="utf-8"

            ) as file:

                messages = file.read()


        except FileNotFoundError:

            return


        if not messages:

            return


        if len(
            messages.strip()
        ) <= 1:

            return


        if old_chat_message == messages:

            return


        self.addMessage(

            message=messages,

            color="white"

        )


        old_chat_message = messages


    # =====================================================
    # STATUS TEXT
    # =====================================================

    def SpeechRecogText(self):

        try:

            with open(

                TempDirectoryPath(
                    "Status.data"
                ),

                "r",

                encoding="utf-8"

            ) as file:

                message = file.read()


            self.label.setText(
                message
            )


        except FileNotFoundError:

            self.label.setText("")


    # =====================================================
    # ADD CHAT MESSAGE
    # =====================================================

    def addMessage(
        self,
        message,
        color
    ):

        cursor = self.chat_text_edit.textCursor()


        char_format = QTextCharFormat()

        block_format = QTextBlockFormat()


        block_format.setTopMargin(10)

        block_format.setLeftMargin(10)


        char_format.setForeground(

            QColor(color)

        )


        cursor.movePosition(
            cursor.End
        )


        cursor.setCharFormat(
            char_format
        )


        cursor.setBlockFormat(
            block_format
        )


        cursor.insertText(

            message + "\n"

        )


        self.chat_text_edit.setTextCursor(
            cursor
        )


        self.chat_text_edit.ensureCursorVisible()


# =========================================================
# INITIAL SCREEN
# =========================================================

class IntialScreen(QWidget):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(parent)


        desktop = QApplication.desktop()


        screen_width = (
            desktop
            .screenGeometry()
            .width()
        )


        screen_height = (
            desktop
            .screenGeometry()
            .height()
        )


        content_layout = QVBoxLayout()


        content_layout.setContentsMargins(

            0,
            0,
            0,
            100

        )


        # -----------------------------------------
        # GIF
        # -----------------------------------------

        self.gif_label = QLabel()


        self.gif_movie = QMovie(

            GraphicsDirectoryPath(
                "Jarvis.gif"
            )

        )


        self.gif_label.setMovie(
            self.gif_movie
        )


        max_gif_size_H = int(

            screen_width
            /
            16
            *
            9

        )


        self.gif_movie.setScaledSize(

            QSize(

                screen_width,

                max_gif_size_H

            )

        )


        self.gif_label.setAlignment(
            Qt.AlignCenter
        )


        self.gif_movie.start()


        self.gif_label.setSizePolicy(

            QSizePolicy.Expanding,

            QSizePolicy.Expanding

        )


        # -----------------------------------------
        # MIC ICON
        # -----------------------------------------

        self.icon_label = QLabel()


        self.icon_label.setFixedSize(

            150,

            150

        )


        self.icon_label.setAlignment(
            Qt.AlignCenter
        )


        self.toggled = True


        self.toggle_icon()


        self.icon_label.mousePressEvent = (
            self.toggle_icon
        )


        # -----------------------------------------
        # STATUS LABEL
        # -----------------------------------------

        self.label = QLabel("")


        self.label.setStyleSheet(

            """
            color:white;
            font-size:16px;
            margin-bottom:0;
            border:none;
            """

        )


        self.label.setAlignment(
            Qt.AlignCenter
        )


        # -----------------------------------------
        # ADD ELEMENTS
        # -----------------------------------------

        content_layout.addWidget(

            self.gif_label,

            alignment=Qt.AlignCenter

        )


        content_layout.addWidget(

            self.label,

            alignment=Qt.AlignCenter

        )


        content_layout.addWidget(

            self.icon_label,

            alignment=Qt.AlignCenter

        )


        self.setLayout(
            content_layout
        )


        self.setFixedHeight(
            screen_height
        )


        self.setStyleSheet(

            "background-color:black;"

        )


        # -----------------------------------------
        # TIMER
        # -----------------------------------------

        self.timer = QTimer(self)


        self.timer.timeout.connect(

            self.SpeechRecogText

        )


        self.timer.start(100)


    # =====================================================
    # STATUS
    # =====================================================

    def SpeechRecogText(self):

        try:

            with open(

                TempDirectoryPath(
                    "Status.data"
                ),

                "r",

                encoding="utf-8"

            ) as file:

                message = file.read()


            self.label.setText(
                message
            )


        except FileNotFoundError:

            self.label.setText("")


    # =====================================================
    # LOAD MIC ICON
    # =====================================================

    def load_icon(

        self,

        path,

        width=60,

        height=60

    ):

        pixmap = QPixmap(path)


        new_pixmap = pixmap.scaled(

            width,

            height,

            Qt.KeepAspectRatio,

            Qt.SmoothTransformation

        )


        self.icon_label.setPixmap(
            new_pixmap
        )


    # =====================================================
    # MIC TOGGLE
    # =====================================================

    def toggle_icon(
        self,
        event=None
    ):

        if self.toggled:

            self.load_icon(

                GraphicsDirectoryPath(
                    "Mic_on.png"
                ),

                60,

                60

            )


            MicButtonInitialed()


        else:

            self.load_icon(

                GraphicsDirectoryPath(
                    "Mic_off.png"
                ),

                60,

                60

            )


            MicButtonClosed()


        self.toggled = not self.toggled


# =========================================================
# MESSAGE SCREEN
# =========================================================

class MessageScreen(QWidget):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(parent)


        desktop = QApplication.desktop()


        screen_width = (

            desktop
            .screenGeometry()
            .width()

        )


        screen_height = (

            desktop
            .screenGeometry()
            .height()

        )


        layout = QVBoxLayout(self)


        layout.setContentsMargins(

            0,
            0,
            0,
            0

        )


        chat_section = ChatSection()


        layout.addWidget(
            chat_section
        )


        self.setStyleSheet(

            "background-color:black;"

        )


        self.setFixedHeight(
            screen_height
        )


        self.setFixedWidth(
            screen_width
        )


# =========================================================
# TOP BAR
# =========================================================

class CustomTopBar(QWidget):

    def __init__(
        self,
        parent,
        stacked_widget
    ):

        super().__init__(parent)


        self.stacked_widget = (
            stacked_widget
        )


        self.draggable = True

        self.offset = None


        self.initUI()


    # =====================================================
    # TOP BAR UI
    # =====================================================

    def initUI(self):

        self.setFixedHeight(50)


        layout = QHBoxLayout(self)


        layout.setContentsMargins(

            5,
            5,
            5,
            5

        )


        layout.setAlignment(
            Qt.AlignRight
        )


        # -----------------------------------------
        # TITLE
        # -----------------------------------------

        title_label = QLabel(

            f" {str(Assistantname).capitalize()} AI "

        )


        title_label.setStyleSheet(

            """
            color:black;
            font-size:18px;
            background-color:white;
            """

        )


        # -----------------------------------------
        # HOME BUTTON
        # -----------------------------------------

        home_button = QPushButton()


        home_button.setIcon(

            QIcon(

                GraphicsDirectoryPath(
                    "Home.png"
                )

            )

        )


        home_button.setText(
            "  Home"
        )


        home_button.setStyleSheet(

            """
            height:40px;
            background-color:white;
            color:black;
            """

        )


        home_button.clicked.connect(

            lambda:
            self.stacked_widget.setCurrentIndex(0)

        )


        # -----------------------------------------
        # CHAT BUTTON
        # -----------------------------------------

        message_button = QPushButton()


        message_button.setIcon(

            QIcon(

                GraphicsDirectoryPath(
                    "chats.png"
                )

            )

        )


        message_button.setText(
            "  Chat"
        )


        message_button.setStyleSheet(

            """
            height:40px;
            background-color:white;
            color:black;
            """

        )


        message_button.clicked.connect(

            lambda:
            self.stacked_widget.setCurrentIndex(1)

        )


        # -----------------------------------------
        # MINIMIZE
        # -----------------------------------------

        minimize_button = QPushButton()


        minimize_button.setIcon(

            QIcon(

                GraphicsDirectoryPath(
                    "Minimize2.png"
                )

            )

        )


        minimize_button.setStyleSheet(

            "background-color:white;"

        )


        minimize_button.clicked.connect(

            self.minimizeWindow

        )


        # -----------------------------------------
        # MAXIMIZE
        # -----------------------------------------

        self.maximize_button = QPushButton()


        self.maximize_icon = QIcon(

            GraphicsDirectoryPath(
                "Minimize2.png"
            )

        )


        self.restore_icon = QIcon(

            GraphicsDirectoryPath(
                "Minimize.png"
            )

        )


        self.maximize_button.setIcon(

            self.maximize_icon

        )


        self.maximize_button.setFlat(
            True
        )


        self.maximize_button.setStyleSheet(

            "background-color:white;"

        )


        self.maximize_button.clicked.connect(

            self.maximizeWindow

        )


        # -----------------------------------------
        # CLOSE
        # -----------------------------------------

        close_button = QPushButton()


        close_button.setIcon(

            QIcon(

                GraphicsDirectoryPath(
                    "close.png"
                )

            )

        )


        close_button.setStyleSheet(

            "background-color:white;"

        )


        close_button.clicked.connect(

            self.closeWindow

        )


        # -----------------------------------------
        # ADD BUTTONS
        # -----------------------------------------

        layout.addWidget(
            title_label
        )


        layout.addStretch(1)


        layout.addWidget(
            home_button
        )


        layout.addWidget(
            message_button
        )


        layout.addStretch(1)


        layout.addWidget(
            minimize_button
        )


        layout.addWidget(
            self.maximize_button
        )


        layout.addWidget(
            close_button
        )


    # =====================================================
    # PAINT
    # =====================================================

    def paintEvent(
        self,
        event
    ):

        painter = QPainter(self)


        painter.fillRect(

            self.rect(),

            Qt.white

        )


        super().paintEvent(
            event
        )


    # =====================================================
    # MINIMIZE
    # =====================================================

    def minimizeWindow(self):

        self.parent().showMinimized()


    # =====================================================
    # MAXIMIZE
    # =====================================================

    def maximizeWindow(self):

        if self.parent().isMaximized():

            self.parent().showNormal()


            self.maximize_button.setIcon(

                self.maximize_icon

            )


        else:

            self.parent().showMaximized()


            self.maximize_button.setIcon(

                self.restore_icon

            )


    # =====================================================
    # CLOSE
    # =====================================================

    def closeWindow(self):

        self.parent().close()


    # =====================================================
    # WINDOW DRAG
    # =====================================================

    def mousePressEvent(
        self,
        event
    ):

        if (
            event.button() == Qt.LeftButton
            and
            self.draggable
        ):

            self.offset = event.pos()


    def mouseMoveEvent(
        self,
        event
    ):

        if (
            self.draggable
            and
            self.offset is not None
            and
            event.buttons() & Qt.LeftButton
        ):

            new_pos = (

                event.globalPos()
                -
                self.offset

            )


            self.parent().move(
                new_pos
            )


    def mouseReleaseEvent(
        self,
        event
    ):

        self.offset = None


# =========================================================
# MAIN WINDOW
# =========================================================

class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()


        self.setWindowFlags(

            Qt.FramelessWindowHint

        )


        self.initUI()


    # =====================================================
    # UI
    # =====================================================

    def initUI(self):

        desktop = QApplication.desktop()


        screen_width = (

            desktop
            .screenGeometry()
            .width()

        )


        screen_height = (

            desktop
            .screenGeometry()
            .height()

        )


        stacked_widget = QStackedWidget(
            self
        )


        intial_screen = IntialScreen()


        message_screen = MessageScreen()


        stacked_widget.addWidget(
            intial_screen
        )


        stacked_widget.addWidget(
            message_screen
        )


        self.setGeometry(

            0,
            0,
            screen_width,
            screen_height

        )


        self.setStyleSheet(

            "background-color:black;"

        )


        top_bar = CustomTopBar(

            self,

            stacked_widget

        )


        self.setMenuWidget(
            top_bar
        )


        self.setCentralWidget(
            stacked_widget
        )


# =========================================================
# START GUI
# =========================================================

def GraphicalUserInterface():

    app = QApplication(
        sys.argv
    )


    window = MainWindow()


    window.show()


    sys.exit(
        app.exec_()
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    GraphicalUserInterface()