import os
import platform
import subprocess
import webbrowser
from PyQt6 import QtWidgets, QtCore, QtGui
from qt_material import apply_stylesheet

import html2md2csv  # own package


class AnkiConverterApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Initialize the output folder
        self.output_folder = "output"
        os.makedirs(self.output_folder, exist_ok=True)

        # Set up the UI
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("GDocs Table format to Anki v0.1.0")
        self.setGeometry(100, 100, 600, 180)

        # Layout
        layout = QtWidgets.QGridLayout(self)

        # Title
        self.app_name = QtWidgets.QLabel("GDocs to Anki Converter")
        self.app_name.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.app_name, 0, 0, 1, 3)

        # File selection label
        self.file_label = QtWidgets.QLabel(
            "Select a zip file from GDocs (must be in a specific format. see Help):"
        )
        layout.addWidget(self.file_label, 1, 0, 1, 3)

        # File path entry and browse button
        self.file_path_entry = QtWidgets.QLineEdit(self)
        layout.addWidget(self.file_path_entry, 2, 0, 1, 3)

        self.browse_button = QtWidgets.QPushButton("Browse", self)
        self.browse_button.clicked.connect(self.browse_files)
        layout.addWidget(self.browse_button, 2, 3)

        # Deck name input
        self.deck_label = QtWidgets.QLabel("Enter Deck Name:")
        layout.addWidget(self.deck_label, 3, 0)

        self.deck_name_entry = QtWidgets.QLineEdit(self)
        layout.addWidget(self.deck_name_entry, 4, 0, 1, 3)

        # Buttons for actions
        self.run_button = QtWidgets.QPushButton("Create .apkg", self)
        self.run_button.clicked.connect(self.run_script)
        layout.addWidget(self.run_button, 4, 3)

        self.open_images_button = QtWidgets.QPushButton("Open Images", self)
        self.open_images_button.clicked.connect(self.open_explorer_script_dir)
        layout.addWidget(self.open_images_button, 5, 0)

        self.open_collections_button = QtWidgets.QPushButton("Open collections.media", self)
        self.open_collections_button.clicked.connect(self.open_explorer_collections_media)
        layout.addWidget(self.open_collections_button, 5, 1)

        self.check_updates_button = QtWidgets.QPushButton("Check for Updates", self)
        self.check_updates_button.clicked.connect(self.check_updates)
        layout.addWidget(self.check_updates_button, 5, 2)

        self.help_button = QtWidgets.QPushButton("Help", self)
        self.help_button.clicked.connect(self.help_page)
        layout.addWidget(self.help_button, 5, 3)

        # credits
        self.credits = QtWidgets.QLabel("made with love for batch syncytium")
        font = QtGui.QFont()
        font.setItalic(True)  # Set font to italic
        self.credits.setFont(font)
        layout.addWidget(self.credits, 6, 0, 1, 3)

    def browse_files(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Zip File", "", "Zip Files (*.zip)")
        if file_path:
            self.file_path_entry.setText(file_path)

    def open_explorer_collections_media(self):
        current_os = platform.system()
        if current_os == "Windows":
            folder = os.path.expanduser('~\\AppData\\Roaming\\Anki2')
            subprocess.Popen(f'explorer "{folder}"')
        elif current_os == "Linux":
            folder = os.path.expanduser('~/.var/app/net.ankiweb.Anki/data/Anki2/')
            subprocess.Popen(['xdg-open', folder])
        elif current_os == "Darwin":
            folder = os.path.expanduser('~/Library/Application Support/Anki2/')
            subprocess.Popen(['open', folder])
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "Unsupported operating system")

    def open_explorer_script_dir(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        current_os = platform.system()
        if current_os == "Windows":
            subprocess.Popen(f'explorer "{script_dir}"')
        elif current_os == "Linux":
            subprocess.Popen(['xdg-open', script_dir])
        elif current_os == "Darwin":
            joined_path = os.path.join(script_dir, 'output')
            subprocess.Popen(['open', joined_path])
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "Unsupported operating system")

    def run_script(self):
        file_path = self.file_path_entry.text()
        deck_name = self.deck_name_entry.text()

        if not file_path:
            QtWidgets.QMessageBox.critical(self, "Error", "Please select a zip file.")
            return

        if not deck_name:
            QtWidgets.QMessageBox.critical(self, "Error", "Please enter a Deck Name.")
            return

        if not file_path.endswith(".zip"):
            QtWidgets.QMessageBox.critical(self, "Error", "Please select a valid zip file.")
            return

        try:
            os.makedirs(self.output_folder, exist_ok=True)
            html2md2csv.main(file_path, deck_name)
            QtWidgets.QMessageBox.information(self, "Success", f"Script completed! Processed file saved in '{self.output_folder}' folder")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def check_updates(self):
        update_url = "https://github.com/gregorylearns/gdocs-to-anki/releases/"
        webbrowser.open(update_url)

    def help_page(self):
        update_url = "https://github.com/gregorylearns/gdocs-to-anki#Usage"
        webbrowser.open(update_url)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    converter_app = AnkiConverterApp()

    apply_stylesheet(app, theme='light_red.xml')

    converter_app.show()

    # Center the window on the screen
    screen = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
    # size = converter_app.geometry()
    # x = (screen.width() - size.width()) // 2
    # y = (screen.height() - size.height()) // 2
    # converter_app.move(x, y)

    app.exec()
