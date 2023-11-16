import PySimpleGUI as sg
import os
import subprocess
import html2md2csv
import webbrowser

# Define the output folder
output_folder = "output"

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)


def open_explorer_collections_media():
    # Folder in %appdata%/Anki2
    folder2 = os.path.expanduser('~\\AppData\\Roaming\\Anki2')

    # Open Windows Explorer to the second folder
    subprocess.Popen(f'explorer "{folder2}"')


def open_explorer_script_dir():
    # Folder in the script's directory
    # folder1 = os.path.join(images_directory)
 
    # Get the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Open Windows Explorer to the first folder
    subprocess.Popen(f'explorer "{script_dir}')

# Define the GUI layout
layout = [
    [sg.Text("(1) Select a zip  file from GDocs (File > Download > HTML):")],
    [sg.Text("NOTE: THE SCRIPT WILL ONLY WORK IF THERE ARE 3-4 COLUMNS,")],
    [sg.Text("First column is discarded, Second column are Front, Third Column is back")],
    [sg.InputText(key="file_path", size=(40, 1)), sg.FileBrowse(file_types=(("Zip Files", "*.zip"),))],
    [sg.Text("(2) Enter Deck Name:"), sg.InputText(key="deck_name")],
    [sg.Button("(3) Run Script")],
    [sg.Text("(4) Move Images from tmp folder to <appdata>\\Anki2\\<user>\\collections.media")],
    [sg.Button("Open images"), sg.Button("Open collections.media"), sg.Button("Check for Updates"), sg.Button("Exit")]
]

# Create the window
window = sg.Window("GDocs Table format to anki v0.0.1", layout, finalize=True)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == "Exit":
        break

    elif event == "Open images":
        open_explorer_script_dir()

    elif event == "Open collections.media":
        open_explorer_collections_media()

    elif event == "Check for Updates":
        # Define the URL to the update page
        update_url = "https://github.com/gregorylearns/gdocs-to-anki/releases/tag/releases"
        # Open the URL in the default web browser
        webbrowser.open(update_url)

    elif event == "(3) Run Script":
        file_path = values["file_path"]
        deck_name = values["deck_name"]


        if not file_path:
            sg.popup_error("Please select a zip file.")
            continue

        if not deck_name:
            sg.popup_error("Please enter a Deck Name.")
            continue

        if not file_path.endswith(".zip"):
            sg.popup_error("Please select an zip file.")
            continue

        # Run your script here, for example:
        # subprocess.run(["pdfexperthighlights2anki.py", file_path, deck_name])
        # Simulate script completion by copying the file to the output folder
        output_folder = "anki_converted"
        # output_path = os.path.join(output_folder, f"{deck_name}.apkg")

        try:
            os.makedirs(output_folder, exist_ok=True)
            with open(file_path, "rb") as source_file:
                html2md2csv.main(file_path, deck_name)
            sg.popup(f"Script completed! Processed file saved in '{output_folder}' folder")

        except Exception as e:
            sg.popup_error(f"An error occurred: {e}")

window.close()
