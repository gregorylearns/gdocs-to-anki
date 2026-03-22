from bs4 import BeautifulSoup
import re
import argparse
import tinycss2
import pprint


# TODO
"""
im using python bs4 help me parse the style text/css as i will reapply it in my own implementation to a simpler html type later 

Would you like me to write a function that automatically replaces these classes with semantic tags like <strong> and <em>?


"""
def parse_gdoc_styles(soup, retain_properties=None):
    """
    Builds a map of class names to style dicts, 
    optionally filtering for specific properties.
    """
    if retain_properties is None:
        # Default properties to keep if none specified
        retain_properties = ["color", "font-weight", "font-style", "text-decoration", "background-color"]

    style_tag = soup.find("style")
    if not style_tag: return {}
    
    rules = tinycss2.parse_stylesheet(style_tag.string, skip_comments=True, skip_whitespace=True)
    style_dict = {}
    
    for rule in rules:
        if rule.type == 'qualified-rule':
            # Selector extraction (e.g., ".c1")
            selector = "".join(str(t.value) for t in rule.prelude if hasattr(t, 'value')).strip('.')
            
            # Declaration extraction (e.g., "font-weight: 700")
            declarations = tinycss2.parse_declaration_list(rule.content)
            
            # Only create entry if we find properties we want to keep
            temp_styles = {}
            for decl in declarations:
                if decl.type == 'declaration' and decl.name in retain_properties:
                    # FIX: Ensure all token values are cast to string before joining
                    val = "".join(str(t.value) for t in decl.value if hasattr(t, 'value')).strip()
                    temp_styles[decl.name] = val
            
            if temp_styles:
                style_dict[selector] = temp_styles
                    
    return style_dict



# def apply_semantic_styles(soup, style_map):
#     """Iterates through spans/elements and wraps them based on style_map."""
#     for element in soup.find_all(class_=True):
#         classes = element.get("class", [])
#         combined_styles = {}
#         for cls in classes:
#             combined_styles.update(style_map.get(cls, {}))
        
#         # Logic to wrap element.contents in <strong>, <em>, <u>, or apply inline colors
#         # based on combined_styles
#         ...

def html_to_markdown(cell, style_map, soup):
    """
    Refined version of html_to_markdown.
    - Unwraps <p> tags to keep only the content.
    - Uses 'soup' to create new tags (fixes TypeError).
    - Maps CSS classes to semantic tags (strong, em, u).
    - Preserves colors via inline styles.
    - Returns ONLY the inner content (removes outer <td> tags).
    """
    print(f"---->")
    print(f"> cell before: {cell}")
 
    # 1. Remove <p> tags but keep their content
    for p in cell.find_all("p"):
        p.append("<br>")
        p.unwrap()


    # 2. Handle links
    for a in cell.find_all("a"):
        link_text = a.get_text(strip=True)
        href = a.get("href", "")
        a.replace_with(f"[{link_text}]({href})")

        # use this soon when refactoring code
        # a.replace_with(f"<a href='{href}'>{link_text}</a>")
        # img.replace_with(f"<img src='{src}'>")
    
    # 3. Handle images
    # TODO remove excess tags
    for img in cell.find_all("img"):
        src = img.get("src", "")
        alt = img.get("alt", "")

        # Create a clean replacement (Markdown or simple HTML)
        # If you want Markdown:
        replacement = f"![{alt}]({src})"
        # If you want clean HTML:
        # replacement = soup.new_tag("img", src=src, alt=alt)
        
        # Check if the image is wrapped in a span (Google Docs style)
        parent = img.parent
        if parent and parent.name == "span":
            # Replace the entire span with the clean image
            parent.replace_with(replacement)
        else:
            # Otherwise just replace the image itself
            img.replace_with(replacement)
        
    
    # # 4. Handle ordered lists
    # for ol in cell.find_all("ol"):
    #     for i, li in enumerate(ol.find_all("li"), start=1):
    #         li.insert_before(f"{chr(64+i)}. ") # use chr() to list out unicode letters in order e.g. ABCDE
    #         li.append("\n")

    # 4. Handle ordered lists (CLEAN VERSION)
    for ol in cell.find_all("ol"):
        for i, li in enumerate(ol.find_all("li"), start=1):
            # Insert your custom numbering
            li.insert_before(f"{chr(64+i)}. ") 
            li.append("<br>") # Use <br> for linebreaks in the list
            # Unwrap the <li> tag
            li.unwrap()
        # Unwrap the <ol> tag
        ol.unwrap()


    # Handle paragraphs with 
    # for p in cell.find_all("p"):
    #     text = p.get_text()  # keep the \n
    #     p.replace_with(text + "\n")


    # Handle italics/bold/underline
    # TODO

    # Finally, get the text with our replacements
    # return cell.get_text()

    # Handle formatting by looking up classes in the style_map
    for span in cell.find_all("span", class_=True):
        classes = span.get("class", [])
        combined_styles = {}
        
        

        # Merge styles if multiple classes are applied
        for c in classes:
            if c in style_map:
                combined_styles.update(style_map[c])
        
        if not combined_styles:
            continue

        
        


        # Remove color:000000 in combined styles
        if combined_styles.get("color") == "000000":
            combined_styles.pop("color", None)
        print(f">>>combined_styles: {combined_styles}")

        
        

        # Apply semantic tags (Order matters: wrap innermost to outermost)
        # 1. Underline
        if "text-decoration" in combined_styles and "underline" in combined_styles["text-decoration"]:
            span.wrap(soup.new_tag("u"))
            
        # 2. Italics
        if combined_styles.get("font-style") == "italic":
            span.wrap(soup.new_tag("em"))
            
        # 3. Bold
        if combined_styles.get("font-weight") in ["700.0", "bold"]:
            span.wrap(soup.new_tag("b"))

        # 4. Colors (Preserve as inline style on the span itself)
        inline_styles = []
        if "color" in combined_styles:
            inline_styles.append(f"color: #{combined_styles['color']}")
        if "background-color" in combined_styles:
            inline_styles.append(f"background-color: {combined_styles['background-color']}")
        
        if inline_styles:
            # Keep the span ONLY if it has a color/background
            span['style'] = "; ".join(inline_styles)
            if 'class' in span.attrs:
                del span['class']
            # Remove the class attribute to keep it clean
            del span['class']
        else:
            # No color? Unwrap the span so only <strong>/<em>/<u> remain
            span.unwrap()

    # 6. FINAL CLEANUP: Remove any remaining <span> tags that don't have a style
    # This catches the <span>This is </span> cases
    for span in list(cell.find_all("span")):
        if not span.has_attr('style'):
            span.unwrap()

    # Note: cell.get_text() will strip the <strong>/<em> tags you just added!
    # To keep them, you should use:
    output =  "".join(str(content) for content in cell.contents)
    if output.endswith("<br>"):
        output = output[:-4]
    
    print(f"> cell contents: {cell.contents}")
    print(f"> cell after: {cell}")
    print(f"> classes: {classes}")
    print(f"> style map: {style_map}")
    print(f"> combined styles after: {combined_styles}")
    print(f"> output: {output}")


    return(output)
    # or a markdown converter that understands these tags.





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

    style_map = parse_gdoc_styles(soup)
    # print(gdoc_styles)
    pp = pprint.PrettyPrinter(depth=2)
    pp.pprint(style_map)



    extracted_data = []
    table_rows = soup.find_all("tr")

    for row in table_rows:
        data_cells = row.find_all("td")
        row_data = []
        for cell in data_cells:
            markdown_text = html_to_markdown(cell, style_map, soup)
            markdown_text = sub_text(markdown_text.strip())

            row_data.append(markdown_text)
        if row_data:
            extracted_data.append(row_data)
    # print(extracted_data)
    return(output_unparsed_md(extracted_data))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="html to md")

    parser.add_argument("-i", "--input", help="Process a HTML", metavar="HTML_FILE")
    args = parser.parse_args()

    out = html_to_md_bs4(args.input)
    print(out)