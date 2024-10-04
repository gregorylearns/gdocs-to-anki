from bs4 import BeautifulSoup



myfile = "test\LMMJ1-1-Title-LQ [1-50]\LMMJ11TitleLQ150.html"

import html2text


def convert_lines_to_table(markdown_content):
    """Convert each line of the Markdown content into a row in a Markdown table."""
    lines = markdown_content.split('\n')
    
    # Start the table with headers (customize these headers as needed)
    table = ['| Line Content |', '| --- |']

    # Add each line as a row in the table
    for line in lines:
        if line.strip():  # Only add non-empty lines
            table.append(f'| {line.replace("|", "\\|")} |')

    return '\n'.join(table)


    
# Load the HTML file
with open(myfile, 'r', encoding='utf-8') as file:
    html_content = file.read()

# Create an instance of the HTML2Text converter
converter = html2text.HTML2Text()

# Preserve line breaks from <br> tags in the Markdown output
converter.body_width = 0  # Avoid wrapping lines to a certain width
converter.ignore_links = False  # Include links in the output
converter.ignore_images = False  # Include images in the output
converter.ignore_tables = False  # Convert tables as well
converter.images_as_html = True
converter.single_line_break = True
# converter.


# Convert the HTML to Markdown
markdown_output = converter.handle(html_content)

# Replace \n with <br> in the Markdown output
markdown_output_with_br = markdown_output.replace('\n', '<br>\n')
markdown_output_with_br = markdown_output_with_br.replace('<br>\n  ', '<br>')
markdown_output_with_br = markdown_output_with_br.replace('<br>\n|', '<br>|')
markdown_output_with_br = markdown_output_with_br.replace('<br>\n<', '<br><')

# Print the Markdown output with <br> tags
print(markdown_output_with_br)

# Optionally, save the Markdown to a file
with open('output.md', 'w', encoding='utf-8') as md_file:
    md_file.write(markdown_output_with_br)
