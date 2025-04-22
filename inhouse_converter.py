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
# h.google_doc = True
# h.google_list_indent = 100

myfile = "CopyofGENPATH_2NDBI_UnitExam8.html"
with open(myfile, 'r') as myh:
    contents = myh.read()
    md = h.handle(contents)

    #TODO: find way to retain the bold and italics flags
    #known bug, any text that occurs after the table gets included in the last card

    # find a pythonic way to do the below!
    # dont do it this way. make nalang an ordered list sa card settings to be letter
    # ol {list-style-type: lower-alpha;}


    # Ordered lists to letters (didnt find a flag for it to auto)
    md = re.sub(r"\n\s\s1\. ","<br>A. ", md)
    md = re.sub(r"\n\s\s2\. ","<br>B. ", md)
    md = re.sub(r"\n\s\s3\. ","<br>C. ", md)
    md = re.sub(r"\n\s\s4\. ","<br>D. ", md)
    md = re.sub(r"\n\s\s5\. ","<br>E. ", md)
    md = re.sub(r"\n\s\s6\. ","<br>F. ", md)
    md = re.sub(r"\n\s\s7\. ","<br>G. ", md)
    md = re.sub(r"\n\s\s8\. ","<br>H. ", md)
    md = re.sub(r"\n\s\s9\. ","<br>I. ", md)
    md = re.sub(r"\n\s\s10\. ","<br>J. ", md)
    
    # need catch- all kay it bugs if unordered list -> *
    # for many test cases
    md = re.sub(r"\n\s\s\* ","<br>* ", md)


    #turn each line into a row
    md = re.sub(r"\n\s*\n","<br>", md)
    md = re.sub(r"\n<td>","<td>", md)
    md = re.sub(r"\n<br>","<br>", md)

    #trim
    md = re.sub(r"</td>  <td>","|", md)
    md = re.sub(r"\|<br>","|", md)
    md = re.sub(r"<br>\|","|", md)
    md = re.sub(r"</td></tr>","", md)
    md = re.sub(r"<tr>  <td>","|", md)
    
    # iterate na per line, 
    # split using "|", and take the last 2 of the split as the front/back
    # of the card

    print(type(md))
    splits = md.split("\n")
    print(len(splits))


    # get the questions
    for line in splits:
        if "|" not in line:
            continue
        else:
            splitting = line.split("|")
            # print(splitting)
            print(f"Front:{splitting[-2]}")
            print(f"Back:{splitting[-1]}")
            print("-----")




with open("html2textoutput.txt", 'w') as outfile:
    outfile.write(md)