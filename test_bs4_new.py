from bs4 import BeautifulSoup
import re
import argparse

# myfile = "test_for_html.html"

def html_to_markdown(cell):
    #HTML to kinda markdown

     # Handle links
    for a in cell.find_all("a"):
        link_text = a.get_text(strip=True)
        href = a.get("href", "")
        a.replace_with(f"[{link_text}]({href})")

        # use this soon when refactoring code
        # a.replace_with(f"<a href='{href}'>{link_text}</a>")
        # img.replace_with(f"<img src='{src}'>")
    
    # Handle images
    for img in cell.find_all("img"):
        src = img.get("src", "")
        alt = img.get("alt", "")
        img.replace_with(f"![{alt}]({src})")
        
    
    # Handle ordered lists
    for ol in cell.find_all("ol"):
        for i, li in enumerate(ol.find_all("li"), start=1):
            li.insert_before(f"{chr(64+i)}. ") # use chr() to list out unicode letters in order
            li.append("\n")

    # Handle paragraphs
    for p in cell.find_all("p"):
        text = p.get_text()  # keep the \n
        p.replace_with(text + "\n")

    # Finally, get the text with our replacements
    return cell.get_text()

def sub_text(md):
    # Substitute text
    substitutions = [
        (r"\n+", "<br>"),
        (r"\n\xa0", ""),
    ]
    for pattern, replacement in substitutions:
        md = re.sub(pattern, replacement, md)
    return(md)

def output_unparsed_md(extracted_data: list) -> str:
    # This is for easy backwards compatibility with other code
    # function to mimic the output of the binary 
    # html2md_linux64 -T -i file.html
    # extracted data is a list of lists
    # extracted_data = [row1 = [col1, col2, col3], row2 = [col1, col2, col3]]
    unparsed_md = ""
    for row in extracted_data:
        new_row = "| " + " | ".join(row) + " |\n"
        unparsed_md += new_row
    return(unparsed_md)

def html_to_md_bs4(htmlfile: str) -> str:
    # Uses bs4 to convert html to md
    # janky implementation of my previous jankier html to md implementation
    
    # Load the HTML file
    with open(htmlfile, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    extracted_data = []
    table_rows = soup.find_all("tr")

    for row in table_rows:
        data_cells = row.find_all("td")
        row_data = []
        for cell in data_cells:
            markdown_text = html_to_markdown(cell)
            markdown_text = sub_text(markdown_text.strip())

            row_data.append(markdown_text)
        if row_data:
            extracted_data.append(row_data)
    print(extracted_data)
    return(output_unparsed_md(extracted_data))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="html to md")

    parser.add_argument("-i", "--input", help="Process a HTML", metavar="HTML_FILE")
    args = parser.parse_args()

    out = html_to_md_bs4(args.input)
    print(out)