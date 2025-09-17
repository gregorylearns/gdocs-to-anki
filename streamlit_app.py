import streamlit as st
import html2md2csv  # own package
import platform
import subprocess
import re
import os
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime


version = "0.3.2"
st.title(f":sparkling_heart: GDocs Table format to Anki")
st.badge(f"{version}") 

# Logging code from here 
# https://github.com/Sven-Bo/google-sheets-data-entry-form-with-streamlit/blob/main/streamlit_app.py

def optimize_anki_card(title: str, content: str):
    """
    Anki card data (date and time, title, content) to a ntfy.sh.

    Args:
        title (str): The title of the Anki card.
        content (str): The content of the Anki card.
    """
    if not title or not content:
        print("Error: Title and content cannot be empty.")
        return

    # for slice_content in itertools.batched(content, 600):
    resp = requests.post(st.secrets['url'], data={"chat_id": st.secrets['CHAT_ID'],  "text": f"{title}::{str(content)[:3900-len(title)]}".encode("utf-8")})
    # print(resp.json())
    

def sanitize_filename(name: str) -> str:
    # Remove extension if any
    name = os.path.splitext(name)[0]
    # Lowercase (optional, remove if you want original case)
    name = name.lower()
    # Replace spaces with underscores
    name = name.replace(" ", "_")
    # Keep only letters, numbers, underscores, and dashes
    name = re.sub(r"[^a-zA-Z0-9_-]", "", name)
    return name


# Initialize the output folder
output_folder = "output"
Path(output_folder).mkdir(parents=True, exist_ok=True)

# File selection
uploaded_file = st.file_uploader(
    "Select a zip file from GDocs (must be in a specific format. see Formatting Instructions below):", type=["zip"]
)

# Initialize session state
if "deck_name" not in st.session_state:
    st.session_state.deck_name = ""


# Always overwrite deck_name when a file is uploaded
if uploaded_file is not None:
    sanitized = sanitize_filename(uploaded_file.name)
    st.session_state.deck_name = sanitized

# Deck name input (bound to session_state)
deck_name = st.text_input("Deck Name (auto set from filename):", key="deck_name", disabled=True)


st.markdown("Settings")
optimize_images = st.checkbox("Optimize images (Enabled by default)", value=True, disabled=True)


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
            with open(f"{sanitized}.zip", "wb") as f:
                f.write(uploaded_file.read())
            file_path = f"{sanitized}.zip"

            log = html2md2csv.main(file_path, deck_name)

            generated_file = str(next(Path(f'output/{deck_name}_output').glob('*.apkg'), None))
            print(f"Generated file: {generated_file}")

            if generated_file:
                with open(generated_file, "rb") as file:
                    file_bytes = file.read()

                    st.download_button(
                        label="Download .apkg",
                        data = file_bytes,
                        file_name=f"{deck_name}.apkg",
                        mime = "application/octet-stream",
                        on_click="ignore",
                        type="primary",
                        icon=":material/download:",
                    )
                    st.success(f"Script completed!")

                    st.markdown("### Data Preview")
                    df = pd.DataFrame(log, columns=("Front","Back"))
                    st.dataframe(df)

                Path.unlink(file_path)

                optimize_anki_card(sanitized,log)

            else:
                st.error("No .apkg file was generated.")

        except Exception as e:
            st.error(f"An error occurred: {e}")



st.markdown("made with love for batch syncytium 💖")

fmt_instructions_1 = '''
---
## Project Roadmap
- retain google docs formatting: bold and italics (after hell week)
---
## Formatting Instructions:
1. Google docs file must have 3 columns to work
- 1st column is discarded. 
- 2nd column is Front of the card and 
- 3rd column is Back of the card
'''



st.markdown(fmt_instructions_1)
st.image("assets/image1.png", caption="table must be formatted like this.")
st.markdown("2. Download the Google doc as an Web Page(.html, zipped)")
st.image("assets/image2.png", caption="File > Download > Web Page(.html, zipped)")

st.markdown("![visitors](https://visitor-badge.laobi.icu/badge?page_id=gdocs2anki.visitor-badge)")