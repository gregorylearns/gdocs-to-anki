import os
import platform
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser
import html2md2csv  # own package
# import sv_ttk  # Assuming you're using the same theme library
import customtkinter


class AnkiConverterApp(customtkinter.CTk):
    def __init__(self, parent):
        super().__init__()
        # ttk.Frame.__init__(self, parent)

        # Initialize the output folder
        self.output_folder = "output"
        os.makedirs(self.output_folder, exist_ok=True)

        # Create widgets
        self.setup_widgets()

    def setup_widgets(self):
        # File selection (in one row)
        self.file_label = customtkinter.CTkLabel(self, text="Select a zip file from GDocs (must be in a specific format. see Help):")
        self.file_label.grid(row=0, column=0, columnspan=3, sticky='w')

        # File path entry and browse button in one row
        self.file_path_entry = customtkinter.CTkEntry(self, width=60)
        self.file_path_entry.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky='w')

        self.browse_button = customtkinter.CTkButton(self, text="Browse", command=self.browse_files)
        self.browse_button.grid(row=1, column=3, padx=10, pady=10, sticky='w')

        # Deck name input
        self.deck_label = customtkinter.CTkLabel(self, text="Enter Deck Name:")
        self.deck_label.grid(row=3, column=0, sticky='w')

        self.deck_name_entry = customtkinter.CTkEntry(self, width=60)
        self.deck_name_entry.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky='w')

        # Buttons for actions
        self.run_button = customtkinter.CTkButton(self, text="Create .apkg", command=self.run_script)
        self.run_button.grid(row=4, column=3, columnspan=2, padx=10, pady=10, sticky='w')

        self.open_images_button = customtkinter.CTkButton(self, text="Open Images", command=self.open_explorer_script_dir)
        self.open_images_button.grid(row=5, column=0, padx=10, pady=10, sticky='w')

        self.open_collections_button = customtkinter.CTkButton(self, text="Open collections.media", command=self.open_explorer_collections_media)
        self.open_collections_button.grid(row=5, column=1, padx=10, pady=10, sticky='w')

        self.check_updates_button = customtkinter.CTkButton(self, text="Check for Updates", command=self.check_updates)
        self.check_updates_button.grid(row=5, column=2, padx=10, pady=10, sticky='w')

        self.check_updates_button = customtkinter.CTkButton(self, text="Help", command=self.check_updates)
        self.check_updates_button.grid(row=5, column=3, padx=10, pady=10, sticky='w')


    def browse_files(self):
        file_path = filedialog.askopenfilename(filetypes=(("Zip Files", "*.zip"),))
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, file_path)

    def open_explorer_collections_media(self):
        current_os = platform.system()

        if current_os == "Windows":
            folder2 = os.path.expanduser('~\\AppData\\Roaming\\Anki2')
            subprocess.Popen(f'explorer "{folder2}"')
        elif current_os == "Linux":
            folder2 = os.path.expanduser('~/.var/app/net.ankiweb.Anki/data/Anki2/')
            subprocess.Popen(['xdg-open', folder2])
        elif current_os == "Darwin":
            folder2 = os.path.expanduser('~/Library/Application Support/Anki2/')
            subprocess.Popen(['open', folder2])
        else:
            messagebox.showerror("Error", "Unsupported operating system")

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
            messagebox.showerror("Error", "Unsupported operating system")

    def run_script(self):
        file_path = self.file_path_entry.get()
        deck_name = self.deck_name_entry.get()

        if not file_path:
            messagebox.showerror("Error", "Please select a zip file.")
            return

        if not deck_name:
            messagebox.showerror("Error", "Please enter a Deck Name.")
            return

        if not file_path.endswith(".zip"):
            messagebox.showerror("Error", "Please select a valid zip file.")
            return

        try:
            os.makedirs(self.output_folder, exist_ok=True)
            html2md2csv.main(file_path, deck_name)
            messagebox.showinfo("Success", f"Script completed! Processed file saved in '{self.output_folder}' folder")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def check_updates(self):
        update_url = "https://github.com/gregorylearns/gdocs-to-anki/releases/"
        webbrowser.open(update_url)


def main():
    root = customtkinter.CTk()
    root.title("GDocs Table format to Anki v0.1.0")

    # Set the theme (assuming you're using sv_ttk)
    # sv_ttk.set_theme("dark")

    app = AnkiConverterApp(root)
    # app.pack(fill="both", expand=True)

    # root.update_idletasks()

    # # Center the window on the screen
    # width, height = root.winfo_width(), root.winfo_height()
    # x = int((root.winfo_screenwidth() / 2) - (width / 2))
    # y = int((root.winfo_screenheight() / 2) - (height / 2))

    # root.minsize(width, height)
    # root.geometry(f"+{x}+{y}")

    app.mainloop()


if __name__ == "__main__":
    main()
