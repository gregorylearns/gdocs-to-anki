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
    output_folder = os.path.join("output", f"{deck_name}_output")
    os.makedirs(output_folder, exist_ok=True)

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(output_folder)

    # Return the path to the output folder
    return output_folder



def cleanup_tmp_directory(tmp_dir):
    # Clean up the temporary directory
    shutil.rmtree(tmp_dir)


def html_to_md_stdout(htmlfile):
    # Uses the html2md executable to convert the html to md
    # I haven't figured out a proper implementation. So far using
    # This binary gives the best and easiest result to parse.

    current_os = platform.system()

    if current_os == "Windows":
        print("Running on Windows")
        binaryfile = "html2md_win64.exe"
        
    elif current_os == "Linux":
        print("Running on Linux")
        binaryfile = "html2md_linux64"


    elif current_os == "Darwin":
        print("Running on MacOS")
        binaryfile = "html2md_darwin_arm64"
        
    else:
        print("Unsupported operating system")


    # Assuming html2md.exe is in the bin/ folder
    html2md_path = os.path.join("bin", binaryfile)
    
    command = [html2md_path, "-T", "-i", htmlfile]
    # print(command)
    md_unparsed = subprocess.check_output(command)# , cwd=current_dir)
    
    return(str(md_unparsed.decode("utf-8")))

def replace_md_img_html_img(field,DECK_TITLE):
    # Replace the image and link reference in the .md file to html image tags
    # image
    pattern = r"!\[\]\(images\/(.*?)\)"
    replacement = fr'<img src="{DECK_TITLE}-\1">'
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
        if len(fields) >= 5:
            formatted_fields = [replace_md_img_html_img(field,DECK_TITLE) for field in fields]
            parsed_product += f"{formatted_fields[2]}|{formatted_fields[3]}<br><br>{formatted_fields[4]}\n"

    return (parsed_product)


def optimize_image(image_path, target_width, quality=85):
    """Optimize and resize the image if necessary."""
    with Image.open(image_path) as img:
        original_width, original_height = img.size

        # Resize if image width is greater than target width
        if original_width > target_width:
            new_height = int((target_width / original_width) * original_height)
            img = img.resize((target_width, new_height), Image.ANTIALIAS)

        # Convert to JPEG format
        if img.mode in ("RGBA", "LA"):
            img = img.convert("RGB")
        
        # Save the optimized image
        img.save(image_path, "jpeg", quality=quality)
        print(f"Optimized and saved {image_path}")


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



def export(parsed_lines):
    # Export to
    filename = f"{DECK_TITLE}-without_media.txt"
    with open(filename, 'w', encoding="utf-8") as output_handle:
        output_handle.write(parsed_lines)    
    print(f"File saved to:{filename} successfully! Please Move the images to anki media folder, and import field. Dont forget to enable HTML in import options")



def generate_apkg(parsed_md_split , deck_name):
    # Get the current date in the format "yyyymmddhhmmss"
    current_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    deck_id = int(current_date)

    deck = genanki.Deck(deck_id, deck_name)
    #TODO: ADD CODE FOR GENANKI TO INCLUDE THE MEDIA FILES
    for card in parsed_md_split:
        if len(card) == 1:
            continue
        note = genanki.Note(model=genanki.BASIC_MODEL, fields=[card[0], card[1]])
        deck.add_note(note)

    # Save the deck to an Anki package (*.apkg) file
    genanki.Package(deck).write_to_file(f'{output_folder}/{deck_name}.apkg')
    print(f"File saved to {output_folder}/{deck_name}-without_media.apkg")
    print("Please Move the images to anki media folder.")

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

    text_for_anki_front_and_back = split_text(parsed_md)
    generate_apkg(text_for_anki_front_and_back, DECK_TITLE)


    #debug:
    # print(text_for_anki_front_and_back)


    # # rename images
    rename_images(tmp_dir)
    print(f"{tmp_dir}")
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
