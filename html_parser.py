import re
from html.parser import HTMLParser


# TODO: Remove p and span tags? change to linebreaks?


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.table_data = []
        self.current_row = []
        self.inside_table = False
        self.inside_row = False
        self.inside_cell = False
        self.inside_ordered_list = False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.inside_table = True
            self.table_data = []  # Reset table data for each table
        elif self.inside_table and tag == "tr":
            self.inside_row = True
            self.current_row = []
        elif self.inside_row and (tag == "td" or tag == "th"):
            self.inside_cell = True
            self.cell_data = ""

        if self.inside_cell:
            if tag == "span" and any(k == "style" and "overflow: hidden" in v for k, v in attrs):
                # Skip this span tag
                return

            if tag == "ol":
                self.inside_ordered_list = True
                self.cell_data += "<ol>"
                return

            if tag == "li" and self.inside_ordered_list:
                self.cell_data += "<li>"
                return

            new_attrs = []
            for k, v in attrs:
                if k not in ("colspan", "rowspan"):
                    new_attrs.append((k, v))
            attrs = new_attrs
            attrs_str = " ".join([f'{k}="{v}"' for k, v in attrs if k not in ("class", "style")])
            self.cell_data += f"<{tag} {attrs_str}>" if attrs_str else f"<{tag}>"
        elif tag in ("td", "th"):
            new_attrs = []
            for k, v in attrs:
                if k not in ("colspan", "rowspan"):
                    new_attrs.append((k, v))
            attrs = new_attrs
            attrs_str = " ".join([f'{k}="{v}"' for k, v in attrs if k not in ("class", "style")])
            self.cell_data += f"<{tag} {attrs_str}>" if attrs_str else f"<{tag}>"

    def handle_endtag(self, tag):
        if tag == "table":
            self.inside_table = False
        elif tag == "tr":
            if self.inside_row:
                self.table_data.append(self.current_row)
            self.inside_row = False
        elif tag == "td" or tag == "th":
            if self.inside_cell:
                self.current_row.append(self.cell_data.strip())
            self.inside_cell = False

        if self.inside_cell:
            if tag == "ol":
                self.inside_ordered_list = False
                self.cell_data += "</ol>"
                return

            if tag == "li" and self.inside_ordered_list:
                self.cell_data += "</li>"
                return
            self.cell_data += f"</{tag}>"

    def handle_data(self, data):
        if self.inside_cell:
            self.cell_data += re.sub(r"\n\s*", "", data)


def parse_table(html_file):
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    parser = TableParser()
    parser.feed(html_content)
    return parser.table_data


if __name__ == "__main__":
    table_data = parse_table("test_for_html.html")
    for row in table_data:
        print(row)

    with open("out.txt", "w") as f:
        for row in table_data:
            for column in row:
                f.write(f"{column}|")
            f.write("\n")
