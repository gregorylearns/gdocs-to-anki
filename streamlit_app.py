import streamlit as st
import html2md2csv  # own package
import platform
import subprocess
from pathlib import Path

version = "0.2.1"

st.title(f"GDocs Table format to Anki v{version}")

# Initialize the output folder
output_folder = "output"
Path(output_folder).mkdir(parents=True, exist_ok=True)

# File selection
uploaded_file = st.file_uploader(
    "Select a zip file from GDocs (must be in a specific format. see Help):", type=["zip"]
)

# Deck name input
deck_name = st.text_input("Enter Deck Name:")

# Run script button
if st.button("Create .apkg"):
    if uploaded_file is None:
        st.error("Please select a zip file.")
    elif not deck_name:
        st.error("Please enter a Deck Name.")
    else:
        try:
            print("trying to convert. opening html2md2csv.main function")
            # Save the uploaded file to a temporary location
            with open("temp.zip", "wb") as f:
                f.write(uploaded_file.read())
            file_path = "temp.zip"

            html2md2csv.main(file_path, deck_name)

            generated_file = str(next(Path(f'output/{deck_name}_output').glob('*.apkg'), None))
            print(f"Generated file: {generated_file}")
            with open(generated_file, "rb") as file:

                st.download_button(
                    label="Download text",
                    data = file,
                    file_name=f"{deck_name}.apkg",
                    mime = "application/vnd.anki",
                    on_click="ignore",
                    type="primary",
                    icon=":material/download:",
                )
            # st.success(f"Script completed! Processed file saved in '{output_folder}' folder")

        except Exception as e:
            st.error(f"An error occurred: {e}")


if st.button("Open Output Folder"):
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    current_os = platform.system()
    if current_os == "Windows":
        subprocess.Popen(f'explorer "{output_dir}"')
    elif current_os == "Linux":
        subprocess.Popen(["xdg-open", str(output_dir)])
    elif current_os == "Darwin":
        joined_path = output_dir / "output"
        subprocess.Popen(["open", str(joined_path)])
    else:
        st.error("Unsupported operating system")

st.markdown("made with love for batch syncytium")
