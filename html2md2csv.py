# coding: utf-8

# May 25, 2023
# For mass conversion of recalls to anki decks
# With help from ate Ger and Rhean
# github.com/gregorylearns
#
# TODO: REMOVE brackets, curly braces in DECK_TITLE # DONE - do tests
# TODO: change the printsigns into logging
# TODO: output folder gets created multiple times e.g. extract_zip_to_output and main

# Standard library
import subprocess
import re
import sys
import argparse
import zipfile
import shutil
import datetime
import platform
from PIL import Image
from pathlib import Path

# pypi library
import genanki

# own library
import test_bs4_new



def extract_zip_to_output(zip_file_path, deck_name):
    # Create the output folder if it doesn't exist
    global output_folder

    # make output folder
    output_folder = Path("output") / f"{deck_name}_output"
    output_folder.mkdir(parents=True, exist_ok=True)

    # make images folder
    images_folder = output_folder / "images"
    images_folder.mkdir(parents=True, exist_ok=True)


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
    images_folder = Path(main_folder) / 'images'

    # Delete the images folder if it exists
    if images_folder.exists():
        shutil.rmtree(str(images_folder))
        print(f"Deleted directory: {images_folder}")
    else:
        print(f"No directory found to delete: {images_folder}")

    # Find and delete the .html file
    html_file_path = next((f for f in Path(output_folder).iterdir() if f.name.endswith('.html')), None)

    if html_file_path and html_file_path.is_file():
        html_file_path.unlink()
        print(f"Deleted file: {html_file_path}")
    else:
        print("No .html file found to delete.")


def replace_md_img_html_img(field,DECK_TITLE):
    # Replace HTML <img> tags with updated src attribute
    # print("Hi")
    html_pattern = r'<img\s+src=["\']images\/(.*?)(\.\w+)["\']\s*/?>'
    html_replacement = fr'<img src="images\\{DECK_TITLE}-\1.jpg"/>'
    field = re.sub(html_pattern, html_replacement, field)


    # Replace the image and link reference in the .md file to html image tags
    # image
    pattern = r"!\[\]\(images\/(.*?)(\.\w+)\)"
    replacement = fr'<img src="{DECK_TITLE}-\1.jpg">'  # Replace extension with .jpg re: optimize image fxn
    newfield = re.sub(pattern, replacement, field)

    # links
    pattern_img = r"\[(.*?)\]\((.*?)\)"
    replacement_img = r'<a href="\2">\1</a>'
    newfield_img = re.sub(pattern_img, replacement_img, newfield)

    # return
    return(newfield_img)

def parse_md(unparsed_md):
    # spaghetti code huhu my bad
    # TODO: improve this code
    # Wait pwede raman ni nga dili negative counting!
    parsed_product = ""
    for line in unparsed_md.split("\n"):
        # split kay its separated by pipes
        fields = line.split("|")
        num_of_fields = len(fields)
        if num_of_fields >= 4: #  | a | a |
            formatted_fields = [replace_md_img_html_img(field,DECK_TITLE) for field in fields if field != ""]
            # parsed_product += f"{formatted_fields[(num_of_fields * -1) + 2]}|{"<br>".join(formatted_fields[(num_of_fields * -1) + 3:])}\n" # old ni
            print(f"-----> {formatted_fields}")
            parsed_product += f"{formatted_fields[-2]}|{formatted_fields[-1]}\n" # new ni

        # if len(fields) >= 5: # | aaa | aaa | aaa | aaa |
        #     formatted_fields = [replace_md_img_html_img(field,DECK_TITLE) for field in fields]
        #     parsed_product += f"{formatted_fields[2]}|{formatted_fields[3]}<br><br>{formatted_fields[4]}\n"
    return (parsed_product)


def optimize_image(image_path, target_width, quality=85):
    """Optimize, resize the image if necessary, and save as .jpg. Deletes .png if input was a .png file."""

    # Get the filename and extension
    image_path_obj = Path(image_path)
    file_name = str(image_path_obj.with_suffix(''))
    file_extension = image_path_obj.suffix

    # Set the new image path with a .jpg extension
    new_image_path = str(Path(file_name).with_suffix('.jpg'))

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
        Path(image_path).unlink()
        print(f"Deleted original PNG file: {image_path}")



def rename_images(directory):

    folder = Path(directory) / 'images'

    if not folder.exists():
        print(f"No image in {folder}. Skipping..")
        return

    for filename in folder.iterdir():
        if DECK_TITLE in filename.name:
            print(f"{DECK_TITLE}-{filename.name} already exists! Skipping...")
            continue
        dst = f"{DECK_TITLE}-{filename.name}"
        src = folder / filename.name
        dst = folder / dst
        print(f"renaming {src} -> {dst}")

        # Maybe add resize function here

        src.rename(dst)
        optimize_image(str(dst), target_width=1920)



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
        str(Path(images_folder) / filename.name)
        for filename in Path(images_folder).iterdir()
        if filename.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
    ]

    # Create a package with the deck and the media files
    package = genanki.Package(deck)

    # Attach the media files to the package
    package.media_files = media_files

    # Save the deck to an Anki package (*.apkg) file
    save_location = f'{output_folder}/{deck_name}.apkg'
    package.write_to_file(save_location)
    print(f"File saved to {save_location}")


def find_html_files_in_folder(folder_path):
    """
    Google docs zip files usually are structured in a way that there is a html file
    in the base directory and an images folder.
    """
    html_files = []
    for root, dirs, files in Path(folder_path).walk():
        for file in files:
            if Path(file).name.endswith('.html'):
                html_files.append(str(root / file))
    return html_files

def split_text(text, line_delimiter='\n', item_delimiter='|') -> list:
    lines = text.split(line_delimiter)
    result = []
    for line in lines:
        items = line.split(item_delimiter)
        result.append([item.strip() for item in items])
    return result

def clean_filename(path): # TODO: merge the two functions above and below
    p = Path(path)
    # Get the stem (filename without extension)
    name_without_ext = p.stem
    # Remove special characters
    cleaned_name = re.sub(r'[^A-Za-z0-9_\- ]+', '', name_without_ext)
    return cleaned_name

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

    base=Path(zip_file).name

    global DECK_TITLE
    # DECK_TITLE = deck_name + "-" + Path(base).with_suffix('').name
    # DECK_TITLE = cleanup_deck_title(DECK_TITLE)

    DECK_TITLE = deck_name

    print(f"Generating anki for {DECK_TITLE}")
    htmlfile = find_html_files_in_folder(f"{output_folder}")

    # title = input_file # <--- maybe add something
    print(f"{htmlfile[0]}")

    # old function
    # unparsed_md = html_to_md_stdout(f"{htmlfile[0]}")

    # New function
    unparsed_md = test_bs4_new.html_to_md_bs4(f"{htmlfile[0]}")


    # Parse the output to markdown table
    parsed_md = parse_md(unparsed_md)

    # rename images
    rename_images(tmp_dir)
    print(f"{tmp_dir}")


    # generate apkg with images
    text_for_anki_front_and_back = split_text(parsed_md)
    generate_apkg(text_for_anki_front_and_back, DECK_TITLE)
    cleanup_directory(output_folder)
    return(text_for_anki_front_and_back)



def main(zip_file, deck_name) -> str:
    # Define the output folder
    output_folder = "output"

    # Create the output folder if it doesn't exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    print("running process_single_file function")
    text = process_single_file(zip_file, deck_name)

    return(text)


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
