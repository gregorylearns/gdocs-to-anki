# coding: utf-8

# May 25, 2023
# For mass conversion of recalls to anki decks
# With help from ate Ger and Rhean
# github.com/gregorylearns

import os
import subprocess
import re
from argparse import ArgumentParser


def html_to_md_stdout(htmlfile):
    # uses the html2md.exe executable to convert the html to md
    # print(htmlfile)
    # current_dir = os.path.dirname(os.path.realpath(__file__))
    command = ["html2md.exe", "-T", "-i", htmlfile]
    # print(command)
    md_unparsed = subprocess.check_output(command)# , cwd=current_dir)
    
    return(str(md_unparsed.decode("utf-8")))

def replace_md_img_html_img(field,DECK_TITLE):
    #image
    pattern = r"!\[\]\(images\/(.*?)\)"
    replacement = fr'<img src="{DECK_TITLE}-\1">'
    newfield = re.sub(pattern, replacement, field)

    #links
    pattern_img = r"\[(.*?)\]\((.*?)\)"
    replacement_img = fr'<a href="\2">\1</a>'
    newfield_img = re.sub(pattern_img, replacement_img, newfield)

    #return
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

def rename_images(directory):
    
    folder = f"{directory}images"

    if os.path.isdir(folder) == False:
        print(f"No image in {DECK_TITLE}. Skipping..")
        return

    for filename in os.listdir(folder):
        if DECK_TITLE in filename:
            print(f"{DECK_TITLE}-{filename} already exists! Skipping...")
            continue
        dst = f"{DECK_TITLE}-{filename}"
        src = f"{folder}\\{filename}"  # foldername/filename, if .py file is outside folder
        dst = f"{folder}\\{dst}"
        print(f"renaming {src} -> {dst}")
        os.rename(src, dst)


def export(parsed_lines):
    # Export to
    filename = f"{DECK_TITLE}-converted.txt"
    with open(filename, 'w', encoding="utf-8") as output_handle:
        output_handle.write(parsed_lines)    
    print(f"File saved to:{filename} successfully! Please Move the images to anki media folder, and import field. Dont forget to enable HTML in import options")

def batch_mode():
    # parser = ArgumentParser()
    # parser.add_argument("-i", "--input-file", action="store")
    # parser.add_argument("-d", "--directory", action="store")
    # args = parser.parse_args()

    #batch mode
    select_folder = False
    while select_folder == False:
        daddy_directory = input("Please input the directory: ")
        if os.path.isdir(daddy_directory) == True:
            select_folder = True

    print("A")
    print("Run the code in the Following directories?")
    baby_directories = os.listdir(daddy_directory)
    for directory in baby_directories:
        print(directory)

    prompt1 = input("[Y]es/[N]o: ")
    if prompt1.lower() == "n":
        return

    for baby in baby_directories:
        working_dir = f"{daddy_directory}\\{baby}\\"
        html = [file for file in os.listdir(working_dir) if ".html" in file][0]
   

        global DECK_TITLE
        DECK_TITLE = html.split(".html")[0]

        # title = input_file # <--- maybe add something
        unparsed_md = html_to_md_stdout(f"{working_dir}{html}") 

        # Parse the output
        parsed_md = parse_md(unparsed_md)
        # print(parsed_md)

        # # rename images
        rename_images(working_dir)

        # # Export
        export(parsed_md)


    return



def main():
    batch_mode()




if __name__ == '__main__':
    main()