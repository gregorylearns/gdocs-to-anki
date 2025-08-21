# For the html to text part
# from markdownify import markdownify as md

# myfile = "CopyofGENPATH_2NDBI_UnitExam8.html"
# with open(myfile, 'r') as handle:


#     print(md(handle, default_title=True,
#     autolinks=False,
#     newline_style='BACKSLASH',
#     escape_misc=True,
#     keep_inline_images_in=['p','c0', 'c1']))


# from bs4 import BeautifulSoup

# myfile = "CopyofGENPATH_2NDBI_UnitExam8.html"

# with open(myfile, 'r') as handle:
#     soup = BeautifulSoup(handle, 'html.parser')

#     print(soup.prettify())

#     # print(soup.get_text())

import html2text
import re

h = html2text.HTML2Text()
h.images_as_html = True
h.body_width = 0
h.unicode_snob = True
h.wrap_tables = False
h.bypass_tables = True
# h.pad_tables = True
h.google_doc = True
# h.google_list_indent = 100

# myfile = "CopyofGENPATH_2NDBI_UnitExam8.html"
myfile = "test_for_html.html"
with open(myfile, 'r') as myh:
    contents = myh.read()
    md = h.handle(contents)

    #TODO: find way to retain the bold and italics flags
    #known bug, any text that occurs after the table gets included in the last card

    # Ordered lists to letters (didnt find a flag for it to auto)
    def replace_numbers_with_letters(match):
        number = int(match.group(1))
        return chr(ord('A') + number - 1) + '. '

    md = re.sub(r"^\s*(\d+)\.\s+", replace_numbers_with_letters, md, flags=re.MULTILINE)

    # need catch- all kay it bugs if unordered list -> *
    # for many test cases
    # md = re.sub(r"\n\s\s\* ","<br>* ", md)


    # Define a list of regex substitutions
    substitutions = [
        (r"\n\s*\n", "<br>"),          # Replace multiple newlines with a single <br>
        # (r"\n<td>", "<td>"),           # Clean up newlines before <td>
        # (r"\n<br>", "<br>"),           # Clean up newlines before <br>
        # # (r"<p[^>]*>", ""),             # Remove paragraph tags
        # # (r"</p>", ""),                 # Remove closing paragraph tags
        # (r"</td>  <td>", "|"),         # Consolidate table cells
        # (r"\|<br>", "|"),              # Clean up pipe and <br>
        # (r"<br>\|", "|"),              # Clean up <br> and pipe
        # (r"</td></tr>", ""),           # Remove closing table data and row
        # (r"<tr>  <td>", "|"),          # Consolidate table rows and data
        # (r"</tr>  </td>", "|"),        # Clean up closing row and data
        # (r"<table[^>]*>", ""),         # Remove table tag
        # (r"</table>", ""),             # Remove closing table tag
        # (r"</td>  <td>","|"),          # trim
        # (r"\|<br>","|"),
        # (r"<br></td>\n",""),
        # (r"</td></tr>",""),
        # (r"<tr>  <td>","|"),
        # (r"</tr>  </td>","|"),
        (r"<tr>\n",""),
        # (r"<td>",""),
        (r"<table[^>]*>", ""), # Remove table tag
        (r"</table>", "")   # Remove closing table tag
        ]

    # Apply all substitutions in a loop
    for pattern, replacement in substitutions:
        md = re.sub(pattern, replacement, md)


    print(md)


    # iterate na per line,
    # split using "|", and take the last 2 of the split as the front/back
    # of the card


    splits = md.split("\n")


    # get the questions
    for line in splits:
        if "|" not in line:
            continue
        else:
            # Use list comprehension for stripping whitespace from parts
            splitting = [part.strip() for part in line.split("|")]
            # print(splitting)
            print(f"{splitting[-2]}")
            print(f"{splitting[-1]}")
            print("-----")




with open("html2textoutput.txt", 'w') as outfile:
    outfile.write(md)
