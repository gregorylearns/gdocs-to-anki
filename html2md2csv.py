# coding: utf-8

# May 25, 2023
# For mass conversion of recalls to anki decks
# With help from ate Ger and Rhean
# github.com/gregorylearns
#
# TODO: REMOVE brackets, curly braces in DECK_TITLE # DONE - do tests
#


import os
import subprocess
import re
import sys
import argparse
import zipfile
import shutil
import tempfile
import datetime
import random
import platform
from time import sleep
from PIL import Image

import genanki

def extract_zip_to_output(zip_file_path, deck_name):
    # Create the output folder if it doesn't exist
    global output_folder

    # make output folder
    output_folder = os.path.join("output", f"{deck_name}_output")
    os.makedirs(output_folder, exist_ok=True)

    # make images folder
    images_folder = os.path.join("output", f"{deck_name}_output", "images")
    os.makedirs(images_folder, exist_ok=True)


    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(output_folder)

    # Return the path to the output folder
    return output_folder


def cleanup_directory(main_folder):
    """
    Cleans up the specified main folder by deleting the images/ folder
    and the .html file within it.

    Parameters:
        main_folder: The path to the main folder containing the images/ folder
                     and the .html file.
    """
    # Path to the images folder
    images_folder = os.path.join(main_folder, 'images')

    # Delete the images folder if it exists
    if os.path.exists(images_folder):
        shutil.rmtree(images_folder)
        print(f"Deleted directory: {images_folder}")
    else:
        print(f"No directory found to delete: {images_folder}")

    # Find and delete the .html file
    html_file_path = next((os.path.join(main_folder, f) for f in os.listdir(main_folder) if f.endswith('.html')), None)
    
    if html_file_path and os.path.isfile(html_file_path):
        os.remove(html_file_path)
        print(f"Deleted file: {html_file_path}")
    else:
        print("No .html file found to delete.")


def html_to_md_stdout(htmlfile):
    # Uses the html2md executable to convert the html to md
    # I haven't figured out a proper implementation. So far using
    # This binary gives the best and easiest result to parse.
    """Converts HTML to Markdown using the appropriate html2md binary."""
    
    # Mapping platform names to binary files
    binaries = {
        "Windows": "html2md_win64.exe",
        "Linux": "html2md_linux64",
        "Darwin": "html2md_darwin_arm64"
    }

    # Get the current OS and corresponding binary
    current_os = platform.system()
    binaryfile = binaries.get(current_os)
    
    if not binaryfile:
        sys.exit(f"Unsupported operating system: {current_os}")
    
    # Construct the path to the binary in the bin/ folder
    html2md_path = os.path.join("bin", binaryfile)
    
    # Command to run the html2md conversion
    command = [html2md_path, "-T", "-i", htmlfile]
    
    try:
        # Execute the command and capture the output
        md_unparsed = subprocess.check_output(command)
        return md_unparsed.decode("utf-8")
    except subprocess.CalledProcessError as e:
        sys.exit(f"Error running command: {e}")
    except FileNotFoundError:
        sys.exit(f"Binary not found: {html2md_path}")



def replace_md_img_html_img(field,DECK_TITLE):
    # Replace the image and link reference in the .md file to html image tags
    # image
    pattern = r"!\[\]\(images\/(.*?)(\.\w+)\)"
    replacement = fr'<img src="{DECK_TITLE}-\1.jpg">'  # Replace extension with .jpg
    newfield = re.sub(pattern, replacement, field)

    # links
    pattern_img = r"\[(.*?)\]\((.*?)\)"
    replacement_img = fr'<a href="\2">\1</a>'
    newfield_img = re.sub(pattern_img, replacement_img, newfield)

    # return
    return(newfield_img)

def parse_md(unparsed_md):

    parsed_product = ""
    for line in unparsed_md.split("\n"):
        # split kay its separated by pipes
        fields = line.split("|")
        if len(fields) >= 5: # | aaa | aaa | aaa | aaa |
            formatted_fields = [replace_md_img_html_img(field,DECK_TITLE) for field in fields]
            parsed_product += f"{formatted_fields[2]}|{formatted_fields[3]}<br><br>{formatted_fields[4]}\n"

    return (parsed_product)


def optimize_image(image_path, target_width, quality=85):
    """Optimize, resize the image if necessary, and save as .jpg. Deletes .png if input was a .png file."""
    
    # Get the filename and extension by splitting at the last dot
    file_name = os.path.splitext(image_path)[0]
    file_extension = os.path.splitext(image_path)[1]
    
    # Set the new image path with a .jpg extension
    new_image_path = f"{file_name}.jpg"
    
    with Image.open(image_path) as img:
        original_width, original_height = img.size

        # Resize if image width is greater than target width
        if original_width > target_width:
            new_height = int((target_width / original_width) * original_height)
            img = img.resize((target_width, new_height), Image.Resampling.LANCZOS)

        # Convert to JPEG format if needed (handles transparency for PNGs)
        if img.mode != 'RGB':
            img = img.convert("RGB")

        # Save the optimized image as .jpg
        img.save(new_image_path, "JPEG", quality=quality)
        print(f"Optimized and saved as {new_image_path}")

    # If the original file was a .png, delete it
    if file_extension.lower() == '.png':
        os.remove(image_path)
        print(f"Deleted original PNG file: {image_path}")



def rename_images(directory):
    
    folder = os.path.join(directory, 'images')

    if os.path.exists(folder) == False:
        print(f"No image in {folder}. Skipping..")
        return

    for filename in os.listdir(folder):
        if DECK_TITLE in filename:
            print(f"{DECK_TITLE}-{filename} already exists! Skipping...")
            continue
        dst = f"{DECK_TITLE}-{filename}"
        src = os.path.join(folder, filename)
        dst = os.path.join(folder, dst)
        print(f"renaming {src} -> {dst}")

        # Maybe add resize function here

        os.rename(src, dst)
        optimize_image(dst, target_width=1920)



def export(parsed_lines):
    # Export to
    filename = f"{DECK_TITLE}-without_media.txt"
    with open(filename, 'w', encoding="utf-8") as output_handle:
        output_handle.write(parsed_lines)    
    print(f"File saved to:{filename} successfully! Please Move the images to anki media folder, and import field. Dont forget to enable HTML in import options")



def generate_apkg(parsed_md_split, deck_name):
    """
    Generates an Anki package (.apkg) from parsed markdown data.

    Parameters:
        parsed_md_split: List of lists containing card information.
        deck_name: Name of the Anki deck to create.
        output_folder: Directory where the .apkg file will be saved.
    """
    # Get the current date in the format "yyyymmddhhmmss"
    current_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    deck_id = int(current_date)

    # Create the Anki deck
    deck = genanki.Deck(deck_id, deck_name)

    # Add notes to the deck
    for card in parsed_md_split:
        if len(card) == 1:
            continue
        note = genanki.Note(model=genanki.BASIC_MODEL, fields=[card[0], card[1]])
        deck.add_note(note)

    # Path to the images folder
    images_folder = f'{output_folder}/images/'

    # Get the list of image files from the images/ folder
    media_files = [
        os.path.join(images_folder, filename)
        for filename in os.listdir(images_folder)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
    ]

    # Create a package with the deck and the media files
    package = genanki.Package(deck)
    
    # Attach the media files to the package
    package.media_files = media_files

    # Save the deck to an Anki package (*.apkg) file
    save_location = f'{output_folder}/{deck_name}.apkg'
    package.write_to_file(save_location)
    print(f"File saved to {save_location}")

def open_explorer_to_folders(tmp_dir):
    # Get the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Folder in the script's directory
    # folder1 = os.path.join(images_directory)
 
    # Folder in %appdata%/Anki2
    folder2 = os.path.expanduser('~\\AppData\\Roaming\\Anki2')

    # Open Windows Explorer to the first folder
    # subprocess.Popen(f'explorer "{script_dir}')
    subprocess.Popen(f'explorer "{output_folder}')


    # Open Windows Explorer to the anki appdata folder
    subprocess.Popen(f'explorer "{folder2}"')


def find_html_files_in_folder(folder_path):
    html_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files

def split_text(text, line_delimiter='\n', item_delimiter='|'):
    lines = text.split(line_delimiter)
    result = []
    for line in lines:
        items = line.split(item_delimiter)
        result.append([item.strip() for item in items])
    return result

def cleanup_deck_title(deck_title):
    # Define a regular expression to match questionable characters
    pattern = r'[\[\(\{<>"\'&%$#@!^*+=\]}\),\s]'
    
    # Remove questionable characters from the deck title
    cleaned_title = re.sub(pattern, '', deck_title)
    
    return(cleaned_title)


def process_single_file(zip_file, deck_name):
    # Your processing logic here
    print(f"Processing file: {zip_file}")

    tmp_dir = extract_zip_to_output(zip_file, deck_name)
    print(f'Files extracted to temporary directory: {tmp_dir}')

    # DECK_TITLE = zip_file.split(".zip")[0][:15]

    base=os.path.basename(zip_file)

    global DECK_TITLE
    DECK_TITLE = deck_name + "-" + os.path.splitext(base)[0]
    DECK_TITLE = cleanup_deck_title(DECK_TITLE)

    print(f"Generating anki for {DECK_TITLE}")
    htmlfile = find_html_files_in_folder(f"{tmp_dir}")

    # title = input_file # <--- maybe add something
    print(f"{htmlfile[0]}")


    unparsed_md = html_to_md_stdout(f"{htmlfile[0]}") 

    # Parse the output
    parsed_md = parse_md(unparsed_md)
    # print(parsed_md)

    # rename images
    rename_images(tmp_dir)
    print(f"{tmp_dir}")


    # generate apkg with images
    text_for_anki_front_and_back = split_text(parsed_md)
    generate_apkg(text_for_anki_front_and_back, DECK_TITLE)
    cleanup_directory(output_folder)


    # open_explorer_to_folders(tmp_dir)

    # # Export
    # export(parsed_md)

    # cleanup_tmp_directory(tmp_dir)


# def process_batch_directory(directory_path):
#     # Your batch processing logic here
#     print(f"Processing directory: {directory_path}")
#     # parser = ArgumentParser()
#     # parser.add_argument("-i", "--input-file", action="store")
#     # parser.add_argument("-d", "--directory", action="store")
#     # args = parser.parse_args()

#     # #batch mode
#     # select_folder = False
#     # while select_folder == False:
#     #     daddy_directory = input("Please input the directory: ")
#     #     if os.path.isdir(daddy_directory) == True:
#     #         select_folder = True

#     daddy_directory = directory_path

#     print("A")
#     print("Run the code in the Following directories?")
#     baby_directories = os.listdir(daddy_directory)
#     for directory in baby_directories:
#         print(directory)

#     prompt1 = input("[Y]es/[N]o: ")
#     if prompt1.lower() == "n":
#         return

#     for baby in baby_directories:
#         working_dir = f"{daddy_directory}\\{baby}\\"
#         html = [file for file in os.listdir(working_dir) if ".html" in file][0]
    

#         global DECK_TITLE
#         DECK_TITLE = html.split(".html")[0]

#         # title = input_file # <--- maybe add something
#         unparsed_md = html_to_md_stdout(f"{working_dir}{html}") 

#         # Parse the output
#         parsed_md = parse_md(unparsed_md)
#         # print(parsed_md)

#         # # rename images
#         rename_images(working_dir)

#         # # Export
#         export(parsed_md)

#     return


def main(zip_file, deck_name):
    

    # Define the output folder
    output_folder = "output"

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    process_single_file(zip_file, deck_name)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Anki Deck Converter")

    # Choose between single-file and batch-directory mode
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--single-file", help="Process a single ZIP file", metavar="ZIP_FILE")
    # group.add_argument("-b", "--batch-directory", help="Process all ZIP files in a directory", metavar="DIRECTORY")

    parser.add_argument("-d", "--deck-name", help="Specify the deck name", required=True)

    args = parser.parse_args()
    if args.single_file:
        process_single_file(args.single_file, args.deck_name)
    # elif args.batch_directory:
    #     process_batch_directory(args.batch_directory)
    main(args.single_file)
